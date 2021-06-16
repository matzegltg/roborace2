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

                                       

###### Initialising the Hardware       

ev3 = EV3Brick()

#Motors
motorA = Motor(Port.A)
motorD = Motor(Port.D)
steerMotor = Motor(Port.B)

#Sensors
distanceSensor = UltrasonicSensor(Port.S4)
lightSensor = ColorSensor(Port.S1)


#Defining some expected constants
normalBrightness = 13 #lightSensor.reflection() #Either by meassuring in a nother helper function or just hard code this magic numbers
normalDistance = 30

maxRot = 70
maxLight = 70
maxDistance = 5

###### Defining some helper functions
#ohne übersetzung -> andere Motorrichtung       
def driveForward(motorA, motorD, speed):
    motorA.run(-speed)
    motorD.run(speed)


#Possible transition functions
def distanceToSteering(distance):
    pass

def lightToSteering(light):
    #To make fancy
    if light > 25:
        return linear(light, 25, -40, 40, -100)
    elif light > 15:
        return linear(light, 13, 0, 25, -40)
    elif light > 10:
        return linear(light, 10, 30, 13, 0)    
    else:
        return linear(light, 2, 100, 10, 30)

def linear(x, x0, y0, x1, y1):
    return (y1 - y0)/(x1 - x0) * (x - x0) + y0



#Function to evaluate how much to steer according to which part of the track the bot is
#@requires everything being initialized the right way
#@ensures motor is not changed

#@returns returns a value in the domain [-70 70] which should be the angle for the wheels (and the raw sensor data)
def getSteeringValue(lightSensor, distanceSensor, oldLight, oldDistance, normalBrightness, normalDistance, rot):
    light = lightSensor.reflection()
    
    distance = distanceSensor.distance()

    

    #Checking for what the current sensor in the map is
    #Alternatively you could also just let one sensor for example the light sensor be dominant (easy implementation)
    #Maybe this is better done seperatly - Try it!
    #mode: 0 - light, 1 - distance, 2 - both
    if distance > maxDistance:
        mode = 0
    elif light > maxLight and distance > 20: #TODO Change -20- : Add the appropriate value for which distance the light should be the color of the tunnel
        mode = 1 
    else:
        mode = 2 
    
    #Could be done in one step but I'm thinking about changing the (findModeTask) somewhere else
    if mode == 0:
        light = lightSensor.reflection()
        steering = lightToSteering(light)
        #change = lightToSteering(abs(light-oldLight))
    elif mode == 1:
        steering = distanceToSteering * (normalDistance - distance) - shiftDistance
        change = distanceToSteering * abs(distance-oldDistance)
    elif mode == 2:
        lightSteering = lightToSteering * (normalBrightness - light) - shiftLight
        distanceSteering = distanceToSteering * (normalDistance - distance) - shiftDistance
        steering = 1/2 *( lightSteering + distanceSteering)
        change = 1/2 * (lightToSteering * abs(light-oldLight) + distanceToSteering * abs(distance-oldDistance))

    #Final calculation
    steering = steering
    #If the change is high don't steer as strong
    #changeFactor = 1/(1 + change) #TODO
    #limitFactor = (1 - rot/maxRot) #TODO
    #If the rotation is already high enough or to high dont change to strong
    #steering = limitFactor * changeFactor * (steering - rot)

    #If we use steerMotor.run_angle: We don't need
    #steering = steering + rot
    #This line of code

    return steering, light, distance
    

    #We could also use a lightToSteering etc. function like:
    #steering = 150*m.asin((0.008*(normalBrightness - currentBrightness))) 
    #Again this is best testet with the robot

    #Another thing to implement is to use old data to calculate the derivative
    
    



#####################################################################
#####     M A I N     P R O G R A M     #############################
#####################################################################

driveForward(motorA, motorD, 250)
light = lightSensor.reflection()
distance = distanceSensor.distance()

while True:
    
    rot = steerMotor.angle()
    
    #To return light and distance is a convention to use it in derivative and also maybe somewhere later
    steering, light, distance = getSteeringValue(lightSensor, distanceSensor, light, distance, normalBrightness, normalDistance,rot)

    
    print("Steuerungswinkel:", steering)
    print("Rotation:", rot)
    steerMotor.run_target(600, steering)
        #try steerMotor.run_angle -angleError and change getSteeringValue
    #wait(10)
