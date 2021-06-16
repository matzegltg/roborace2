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

                                       
###########################################################
###### Initialising the Hardware     ######################    
###########################################################
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
    

###########################################################    
###### Defining some helper functions     #################
###########################################################

def driveForward(motorA, motorD, speed):
    motorA.run(-speed)
    motorD.run(-speed)


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
    return (sum(arr) - max(arr))/len(arr)


def linear(x, x0, y0, x1, y1):
    return (y1 - y0)/(x1 - x0) * (x - x0) + y0


def lightToSteering(light):
    #Reminder for Steering:
    #Left - pos.  & Right - neg.
    #Values between [-90 100]

    #Reminder for Light Sensor:
    #High - bright  &  Low - dark
    #values in [2 40]

    #If dark we steer left (2 -> 100) and vice versa (40 -> -90)

    #Linear interpolation
    #vk < v(k+1)
    # v - value,  s - steering

    ### Input Data ###
    v0 = 2
    s0 = 100

    v1 = 10
    s1 = 30

    v2 = 13
    s2 = 0

    v3 = 25
    s3 = -60

    v4 = 40
    s4 = -90
    
    #################

    if light > v4:
        return s4
    if light > v3:
        return linear(light, v3, s3, v4, s4)
    elif light > v2:
        return linear(light, v2, s2, v3, s3)
    elif light > v1:
        return linear(light, v1, s1, v2, s2)    
    else:
        return linear(light, v0, s0, v1, s1)
    

def distanceToSteering(distance):
    #Reminder for Steering:
    #Left - pos.  & Right - neg.
    #Values between [-90 100]

    #Reminder for Distance Sensor:
    #Distance in mm and obviously the more the further away

    #If close we drive right (50 (mm) -> -70)
    
    #Linear interpolation
    #vk < v(k+1)
    # v - value,  s - steering


    ### Input Data ###

    v0 = 0
    s0 = -90

    v1 = 140
    s1 = -30

    v2 = 190
    s2 = 0

    v3 = 400
    s3 = 40

    v4 = 500
    s4 = 80

    ###################

    if distance > v4:
        return s4
    if distance > v3:
        return linear(distance, v3, s3, v4 , s4)
    elif distance > v2:
        return linear(distance,v2, s2 , v3, s3)
    elif distance > v1:
        return linear(distance, v1, s1, v2, s2)
    else:
        return linear(distance, v0, s0, v1, s1)



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
    
 
    
###########################################################
###########    M A I N     P R O G R A M     ##############
###########################################################

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