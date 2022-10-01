#include<Servo.h>
#define ser 2
#define MR D7
#define ML D8

byte incomingByte; // for incoming serial data
Servo myservo;

void setup() {

  myservo.attach(2);
  pinMode(ser, OUTPUT);
  pinMode(MR, OUTPUT);
  pinMode(ML, OUTPUT);
  //pinMode(LED,OUTPUT);
  Serial.begin(115200); // opens serial port, sets data rate to 9600 bps
  digitalWrite(2, HIGH);
  for (int pos = 0; pos <= 180; pos += 3) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(5);                       // waits 15ms for the servo to reach the position
  }
}

void loop() {
  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.parseInt();
    //Serial.println(incomingByte);
  }
  if (incomingByte == 1) {
    digitalWrite(MR, LOW);
    digitalWrite(ML, HIGH);
    delay(3000);
    digitalWrite(ML, LOW);
    digitalWrite(MR, HIGH);
    delay(3000);
    int pos;
    for (pos = 180; pos >= 0; pos -= 3) { // goes from 180 degrees to 0 degrees
      myservo.write(pos);              // tell servo to go to position in variable 'pos'
      delay(5);                       // waits 15ms for the servo to reach the position
    }
    delay(4000);
    for (pos = 0; pos <= 180; pos += 3) { // goes from 0 degrees to 180 degrees
      // in steps of 1 degree
      myservo.write(pos);              // tell servo to go to position in variable 'pos'
      delay(5);                       // waits 15ms for the servo to reach the position
    }
    /*for(pos = 0;pos <= 90;pos++){
      Servo operating
      }*/
    digitalWrite(ML, LOW);
    digitalWrite(MR, LOW);
    incomingByte = 0;
  }
}
