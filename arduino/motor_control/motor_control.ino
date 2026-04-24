#define ENA 10
#define ENB 5
#define IN1 9
#define IN2 8
#define IN3 7
#define IN4 6

void setup() {
  pinMode(ENA,OUTPUT); pinMode(ENB,OUTPUT);
  pinMode(IN1,OUTPUT); pinMode(IN2,OUTPUT);
  pinMode(IN3,OUTPUT); pinMode(IN4,OUTPUT);
  stopAll(); Serial.begin(9600);
}

void forward(int spd) {
  analogWrite(ENA,spd); analogWrite(ENB,spd);
  digitalWrite(IN1,LOW); digitalWrite(IN2,HIGH);
  digitalWrite(IN3,HIGH); digitalWrite(IN4,LOW);
}

void backward(int spd) {
  analogWrite(ENA,spd); analogWrite(ENB,spd);
  digitalWrite(IN1,HIGH); digitalWrite(IN2,LOW);
  digitalWrite(IN3,LOW); digitalWrite(IN4,HIGH);
}

void turnLeft(int spd) {
  analogWrite(ENA,spd); analogWrite(ENB,spd);
  digitalWrite(IN1,HIGH); digitalWrite(IN2,LOW);
  digitalWrite(IN3,HIGH); digitalWrite(IN4,LOW);
}

void turnRight(int spd) {
  analogWrite(ENA,spd); analogWrite(ENB,spd);
  digitalWrite(IN1,LOW); digitalWrite(IN2,HIGH);
  digitalWrite(IN3,LOW); digitalWrite(IN4,HIGH);
}

void stopAll() {
  analogWrite(ENA,0); analogWrite(ENB,0);
  digitalWrite(IN1,LOW); digitalWrite(IN2,LOW);
  digitalWrite(IN3,LOW); digitalWrite(IN4,LOW);
}

void loop() {
  if(Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if(cmd == "F") forward(150);
    else if(cmd == "B") backward(150);
    else if(cmd == "L") turnLeft(150);
    else if(cmd == "R") turnRight(150);
    else if(cmd == "S") stopAll();
  }
}
