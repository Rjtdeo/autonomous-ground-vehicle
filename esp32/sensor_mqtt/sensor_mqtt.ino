#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";
const char* mqtt_server = "10.0.0.246";

#define FRONT_TRIG 26
#define FRONT_ECHO 25
#define LEFT_TRIG 14
#define LEFT_ECHO 27
#define RIGHT_TRIG 12
#define RIGHT_ECHO 13
#define MAX_ULTRASONIC 200.0
#define MAX_RADAR 400.0

Adafruit_MPU6050 mpu;
HardwareSerial gpsSerial(2);
HardwareSerial radarSerial(1);
uint8_t rbuf[32]; int ridx=0; float radarDist=-1.0;
WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED) { delay(500); }
}

void reconnect() {
  while(!client.connected()) {
    if(client.connect("ESP32Rover")) break;
    delay(5000);
  }
}

float getDistance(int trig, int echo) {
  digitalWrite(trig, LOW); delayMicroseconds(2);
  digitalWrite(trig, HIGH); delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long d = pulseIn(echo, HIGH, 30000);
  float cm = d * 0.034 / 2;
  return (cm <= 0 || cm > MAX_ULTRASONIC) ? -1.0 : cm;
}

void setup() {
  Serial.begin(115200);
  pinMode(FRONT_TRIG,OUTPUT); pinMode(FRONT_ECHO,INPUT);
  pinMode(LEFT_TRIG,OUTPUT); pinMode(LEFT_ECHO,INPUT);
  pinMode(RIGHT_TRIG,OUTPUT); pinMode(RIGHT_ECHO,INPUT);
  Wire.begin(21, 22);
  mpu.begin();
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  gpsSerial.begin(9600, SERIAL_8N1, 16, 17);
  radarSerial.begin(256000, SERIAL_8N1, 2, 15);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if(!client.connected()) reconnect();
  client.loop();
  float front = getDistance(FRONT_TRIG, FRONT_ECHO);
  float left = getDistance(LEFT_TRIG, LEFT_ECHO);
  float right = getDistance(RIGHT_TRIG, RIGHT_ECHO);
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  String gps = "";
  while(gpsSerial.available()) {
    char c = gpsSerial.read();
    if(c == '\n') break;
    gps += c;
  }
  String msg = "{";
  msg += "\"front\":" + String(front,1) + ",\"left\":" + String(left,1) + ",\"right\":" + String(right,1) + ",";
  msg += "\"ax\":" + String(a.acceleration.x,2) + ",\"ay\":" + String(a.acceleration.y,2) + ",\"az\":" + String(a.acceleration.z,2) + ",";
  msg += "\"gx\":" + String(g.gyro.x,2) + ",\"gy\":" + String(g.gyro.y,2) + ",\"gz\":" + String(g.gyro.z,2) + ",";
  msg += "\"temp\":" + String(temp.temperature,1) + ",";
  msg += "\"radar\":" + String(radarDist,1) + ",\"gps\":\"" + gps + "\"";
  msg += "}";
  client.publish("rover/sensors", msg.c_str());
  delay(200);
}
