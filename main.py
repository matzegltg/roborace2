#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile, Font
import math as m
import time


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

def execute(motorA, motorD, lenkMotor, lightSensor, ev3):
    normalBrightness = lightSensor.reflection()
    maxLenk = 70
    SteeringValues = [0]
    driveForward(motorA, motorD)
    k = 0
    
    print("hahas")
    while True:
        
        #mesures ausgangswinkeldifferenz
        rotation = lenkMotor.angle()
        print("Das ist die Rotation: " + str(rotation))
        currentBrightness = lightSensor.reflection()
        steering = 150*m.asin((0.008*(normalBrightness - currentBrightness))) 
        SteeringValues.append(steering)    
        backSteering = 2*(SteeringValues[-2] - SteeringValues[-1])
        
        if (rotation < maxLenk):
            if (rotation > (-1)*maxLenk):
                #backSteering = -1/10*(0.02*rotation)**7 * steering
                lenkMotor.run_angle(90,steering - backSteering)
                print("Das hab ich gelenkt: " + str(steering-backSteering))
                #lenkMotor.run_angle(90,backSteering)
            else:
                #wil zu sehr nach rechts, VZ stimmt
                k = 1
                print("Das ist reseteter Winkel: " + str(steering-backSteering))
                ev3.speaker.beep()
                lenkMotor.run_angle(180,-1*(steering-backSteering))
        elif (k == 0):             
            ev3.speaker.beep()
            lenkMotor.run_angle(180,+1*(steering-backSteering))
            print("Das ist reseteter Winkel: " + str(steering-backSteering))
        k = 0
                
                    
def test(motorA, motorD, lenkMotor):
    driveForward(motorA, motorD)
    time.sleep(3)
    lenkMotor.run_angle(90,50)
    time.sleep(1)
    ev3.speaker.beep()
    lenkMotor.run_angle(90,-50)
             
                    
        
def driveForward(motorA, motorD):
    motorA.run(100)
    motorD.run(-100)
    

        
# Create your objects here.
ev3 = EV3Brick()

motorA = Motor(Port.A)
motorD = Motor(Port.D)

lenkMotor = Motor(Port.B)

lightSensor = ColorSensor(Port.S4)

execute(motorA, motorD, lenkMotor, lightSensor, ev3)
#test(motorA, motorD, lenkMotor)
