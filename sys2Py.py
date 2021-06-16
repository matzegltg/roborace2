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
motorA = Motor(Port.C)
motorD = Motor(Port.D)
steerMotor = Motor(Port.B)

#Sensors
distanceSensor = UltrasonicSensor(Port.S3)
lightSensor = ColorSensor(Port.S2)


#Defining some expected constants
normalBrightness = 13 #lightSensor.reflection() #Either by meassuring in a nother helper function or just hard code this magic numbers
normalDistance = 190

maxRot = 70
maxLight = 70
maxDistance = 500

storageLight = []
storageDistance = []
distanceFilter = [0, 0, 0, 0, 0]
for i in range(50):
    storageLight.append(normalBrightness)
    storageDistance.append(normalDistance)
    
    
###### Defining some helper functions
       
def driveForward(motorA, motorD, speed):
    motorA.run(-speed)
    motorD.run(-speed)

#
def driveSteering(motorA, motorD,  speed, steering):
    differential = steering
    
    if steering < 0:
        motorD.run(-speed + differential)
        motorA.run(-speed - differential)
    else:
        motorD.run(-speed - differential)
        motorA.run(-speed + differential)
#Function to add value to storage of data
def shift(arr, val):
    for i in range(len(arr) - 1):
        arr[i + 1] = arr[i]
    arr[0] = val
    return arr

def mean(arr):
    return sum(arr)/len(arr)
        
def filterDistance(arr):
    xMax = arr[0]
    sums = 0
    argMax = 0
    for i in range(1,len(arr)):
        if xMax < arr[i]:
            xMax = arr[i]
            argMax = i
    
    for i in range(len(arr)):
        if i != argMax:
           sums += arr[i]
    return sums/(len(arr)-1)

def lightToSteering(light):   
    if light > 40:
        return -80
    if light > 25:
        return linear(light, 25, -60, 40, -90)
    elif light > 15:
        return linear(light, 13, 0, 25, -60)
    elif light > 10:
        return linear(light, 10, 30, 13, 0)    
    else:
        return linear(light, 2, 100, 10, 30)
    
    
def distanceToSteering(distance):
    if distance > 500:
        return 80
    if distance > 250:
        return linear(distance, 400, 40, 500 , 80)
    elif distance > 190:
        return linear(distance,320, 0 , 400, 40)
    elif distance > 140:
        return linear(distance, 240, -30, 320, 0)
    else:
        return linear(distance, 0, -100, 240, -30)


def linear(x, x0, y0, x1, y1):
    return (y1 - y0)/(x1 - x0) * (x - x0) + y0


#Checking for what the current sensor in the map is
#mode: light, distance,    # transLtoD, transDtoL
def getMode(light, distance, oldMode):
    if light > maxLight and distance > 20: #TODO Change -20- : Add the appropriate value for which distance the light should be the color of the tunnel
        print('Joni ist im Tunnel')
        return 'tunnel'
    elif distance > maxDistance:
        print('högedüge')
        return 'tunnel'
    else:
        print('Ich bin toll')
        return 'tunnel'




#Function to evaluate how much to steer according to which part of the track the bot is
#@requires everything being initialized the right way
#@ensures motor is not changed

#@returns returns a value in the domain [-70 70] which should be the angle for the wheels (and the raw sensor data)
def getSteeringValue(rot, storageLight, oldMode, distanceFilter, storageDistance):
    steering = 0
    light = lightSensor.reflection()
    distance = distanceSensor.distance()
    print('Distance: ', distance)
    
    
    mode = 'light' #getMode(light,distance, oldMode)


    if mode == 'light':
        steering = lightToSteering(light)
        #print(storageLight)
        storageLight = shift(storageLight, light)
        meanLight = mean(storageLight)
        change = meanLight - light
        print("change" + str(change))
        
    elif mode == 'tunnel':
        distanceFilter = shift(distanceFilter, distance)
        filteredValue = filterDistance(distanceFilter)
        steering = distanceToSteering(filteredValue)
        
        storageDistance = shift(storageDistance, distance)
        meanDistance = mean(storageDistance)
        change = meanDistance - distance
        
        
    elif mode == 'transition':
        lightSteering = lightToSteering * (normalBrightness - light) - shiftLight
        distanceSteering = distanceToSteering * (normalDistance - distance) - shiftDistance
        steering = 1/2 *( lightSteering + distanceSteering)
        change = 1/2 * (lightToSteering * abs(light-oldLight) + distanceToSteering * abs(distance-oldDistance))


    
    changeFactor = 1.5
    expectedValue = steering + changeFactor * change
    if expectedValue <= 100:
        if expectedValue >= -100:
            steering = expectedValue
     
    

    return steering, mode
    
 
    
#####################################################################
###########    M A I N     P R O G R A M     #############################
#####################################################################

driveForward(motorA, motorD, 200)
light = lightSensor.reflection()
distance = distanceSensor.distance()
mode = 'light'
for i in range(5):
    distanceFilter[i] = distance
    


while True:
    
    rot = steerMotor.angle()
    
    
    steeringVal, mode = getSteeringValue(rot, storageLight, mode, distanceFilter, storageDistance)
    
    driveSteering(motorA, motorD, 200, steeringVal)
    print("Steering val: " + str(steeringVal))

    steerMotor.run_target(600, steeringVal)
    #try steerMotor.run_angle -angleError and change getSteeringValue
    #wait(100)

#### TO DO ####

# Ultraschall Fehlerhafte Messungen Filtern