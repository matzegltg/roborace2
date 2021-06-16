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

ev3 = EV3Brick()

#Sensors
distanceSensor = UltrasonicSensor(Port.S4)

values = []

for i in range(1000):
    distance = distanceSensor.distance()
    print(distance)
    values.append(distance)

ev3.speaker.beep()



    
    