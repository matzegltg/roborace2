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
import random

steerMotor = Motor(Port.B)
lightSensor = ColorSensor(Port.S1)
ev3 = EV3Brick()
'''
def getAngleInPosition(steerMotor):
    ##########
    #To Do ###
    ##########
    
    steerMotor.run_target(90,0)
    return 0.0
    ##########
'''
notes = ['C4/4', 'C4/4', 'G4/4', 'G4/4']
ev3.speaker.play_notes(notes, tempo=120)

'''
for i in range(20):
    x = random.randint(-100,100)
    steerMotor.run_target(90,x)
    y = random.randint(-100,100)
    steerMotor.run_target(90, y)
    steerMotor.run_target(90,0)
    ev3.speaker.beep()
    wait(7)
    '''