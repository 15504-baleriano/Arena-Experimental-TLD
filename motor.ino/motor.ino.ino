/*
	Capitulo 31 de Arduino desde cero en Español.
	Programa que utiliza la Libreria Stepper para el control de un motor unipolar
	de 5 hilos modelo 28BYJ-48 y su correspondiente driver ULN2003. Se establece una
	velocidad de 2 RPM y un total de 512 pasos equivalentes a un cuarto de vuelta.

	Autor: bitwiseAr  

*/

#include <Stepper.h>			// incluye libreria stepper
int stepperRevolution = 2048; // 2048 es el número de pasos para una vuelta completa del motor
int motSpeed = 15; // numero de pasos por minuto, maximo 15 (velocidad del motor)
Stepper motor0 (stepperRevolution, 18,20,19,21);
Stepper motor1 (stepperRevolution, 8, 10, 9, 11);  	// pasos completos
Stepper motor2 (stepperRevolution, 4,6,5,7);
Stepper motor3 (stepperRevolution, 14,16,15,17);
Stepper motor4 (stepperRevolution, 2,12,3,13);
Stepper motor5 (stepperRevolution, 30,34,32,36);

int dt = 1000;

void setup() {
  motor0.setSpeed(motSpeed);
  motor1.setSpeed(motSpeed);
  motor2.setSpeed(motSpeed);   		// en RPM (valores de 1, 2 o 3 para 28BYJ-48)
  motor3.setSpeed(motSpeed);
  motor4.setSpeed(motSpeed);   		// en RPM (valores de 1, 2 o 3 para 28BYJ-48)
  motor5.setSpeed(motSpeed);
  Serial.begin(9600);
}

void loop() {
  if(Serial.available()>0){
    char valor=Serial.read();
    if(valor=='a'){
    motor0.step(stepperRevolution*1.5);
    delay(dt);
    motor0.step(-stepperRevolution*1.5);
    delay(dt);
    }
    if(valor=='s'){
    motor1.step(stepperRevolution*1.5);
    delay(dt);
    motor1.step(-stepperRevolution*1.5);
    delay(dt);
    }
    if(valor=='d'){
    motor2.step(stepperRevolution*1.5);
    delay(dt);
    motor2.step(-stepperRevolution*1.5);
    delay(dt);
    }
    if(valor=='f'){
    motor3.step(stepperRevolution*1.5);
    delay(dt);
    motor3.step(-stepperRevolution*1.5);
    delay(dt);
    }
    if(valor=='g'){
    motor4.step(stepperRevolution*1.2);
    delay(dt);
    motor4.step(-stepperRevolution*1.2);
    delay(dt);
    }
    if(valor=='h'){
    motor5.step(stepperRevolution*1.5);
    delay(dt);
    motor5.step(-stepperRevolution*1.5);
    delay(dt);
    }
  }

}