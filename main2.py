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
    rotation = 0
    steering = 0
    backSteering = 0
    # Lenkung nach links: steering pos
    # Lenkung nach rechts: steering neg 
    
    while True:
        
        
        rotation = rotation + (steering - backSteering)
        print("Rotation" + str(rotation))
        currentBrightness = lightSensor.reflection()
        brightDiff = normalBrightness - currentBrightness
        if abs(brightDiff) < 5:
            steering  = brightDiff
        else: 
            steering = 0.02*brightDiff**3
            
        print("Das ist die Brightnessdiff: " + str(normalBrightness - currentBrightness))
        SteeringValues.append(steering) 
        
        if (normalBrightness - currentBrightness) == 0:
            backSteering = 0
        else:
            if (abs(rotation) < 70):
                backSteering = 0.5*(SteeringValues[-2] - SteeringValues[-1])
            else:
                backSteering = 20*(SteeringValues[-2] - SteeringValues[-1])
        
        if (rotation > maxLenk):
            if (normalBrightness - currentBrightness) > 0:  
                print("Das ist Winkel vor Reset: (pos. BDiff)" + str(lenkMotor.angle()))
                lenkMotor.run_angle(180,-2*(steering-backSteering))
                print("Das ist reseteter Winkel: " + str(lenkMotor.angle()))
            else:
                print("Das ist Winkel vor Reset: (neg. BDiff)" + str(lenkMotor.angle()))
                lenkMotor.run_angle(180,2*(steering-backSteering))
                print("Das ist reseteter Winkel: " + str(lenkMotor.angle()))
        
        #zu sehr nach rechts
        if (rotation < -1*maxLenk):
            if (normalBrightness - currentBrightness) < 0:
                print("Das ist Winkel vor Reset (neg. BDiff): " + str(lenkMotor.angle()))
                lenkMotor.run_angle(180,-2*(steering-backSteering))
                print("Das ist reseteter Winkel: " + str(lenkMotor.angle()))
            else:
                print("Das ist Winkel vor Reset (pos. BDiff): " + str(lenkMotor.angle()))
                lenkMotor.run_angle(180,2*(steering-backSteering))
                print("Das ist reseteter Winkel: " + str(lenkMotor.angle()))
            
        
        else:
            lenkMotor.run_angle(90,steering - backSteering)
            print("Das hab ich gelenkt: " + str(steering-backSteering))
                
                    
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
