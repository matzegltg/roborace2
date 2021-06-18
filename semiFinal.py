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

#Possible
from storage import Storage

                                       
###########################################################
###### Initialising the Hardware     ######################    
###########################################################
ev3 = EV3Brick()

#Motors
motorLeft = Motor(Port.D)
motorRight = Motor(Port.C)
steerMotor = Motor(Port.B)

#Sensors
distanceSensor = UltrasonicSensor(Port.S3)
lightSensor = ColorSensor(Port.S2)


#Defining some expected constants
normalBrightness = 13 #lightSensor.reflection() #Either by meassuring in a nother helper function or just hard code this magic numbers
normalDistance = 190

maxRot = 90
maxLight = 70
maxDistance = 200

storageLight = []
storageDistance = []
distanceFilter = [0, 0, 0, 0, 0]
for i in range(50):
    storageLight.append(normalBrightness)
    storageDistance.append(normalDistance)
    

###########################################################    
###### Defining some helper functions     #################
###########################################################

def driveForward(motorLeft, motorRight, speed):
    motorLeft.run(-speed)
    motorRight.run(-speed)


def driveDifferential(motorLeft, motorRight,  speed, steering):
    differential = speed/(maxRot * 2) * steering #Maximum differential 1/4 of speed
    
    motorLeft.run(-speed + differential)
    motorRight.run(-speed - differential)
    


#Function to shift value to storage of data
def shift(arr, val):
    for i in range(1,len(arr)):
        arr[-i] = arr[-(i+1)] #second last is mapped to last ...
    arr[0] = val

def mean(arr):
    return sum(arr)/len(arr)
        
def filter(arr):
    return (sum(arr) - max(arr))/len(arr)

#Evaluates a linear function defined by two given points
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

    val =   [0  ,  10,  13,  25,  40]
    steer = [100,  30,   0, -60, -90]

    for i in range(1,len(val)): #Checks if distance is in between some interval of val (can't be <0)
        if light < val[i]:
            return linear(light, val[i-1], steer[i-1], val[i], steer[i])
    
    return steer[-1] #This is the last element 
    '''
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
    '''
    

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

    #even shorter
    
    val =   [  0,  50, 140, 190, 400, 500]
    steer = [-90, -90, -40,   0,  40,  80]

    for i in range(1,len(val)): #Checks if distance is in between some interval (can't be <0)
        if distance < val[i]:
            return linear(distance, val[i-1], steer[i-1], val[i], steer[i])
    
    return steer[-1] #This is the last element 
    '''


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
    '''


#TODO
def changeToSteeringLight():
    pass

def changeToSteeringDist():
    pass


#Checking for what the current sensor in the map is
#mode: light, tunnel,    # transLtoD, transDtoL
def getMode(oldMode):
    #Cyclic method
    light = storageLight[0]
    distance = storageDistance[0]
    print(light,distance)
    if oldMode == 'light':
        if distance < maxDistance:
            print('lt')
            return 'transLtoT'
    elif oldMode == 'transLtoT':
        if light > maxLight:
            print('t')
            return 'tunnel'
    elif oldMode == 'tunnel':
        if light < maxLight:
            return 'transTtoL'
            print('tl')
    elif oldMode == 'transTtoL':
        if distance > maxDistance:
            return 'light'
            print('l')
    return oldMode
    '''
    This is the not cyclic method

    if light > maxLight and distance > 20: #TODO Change -20- : Add the appropriate value for which distance the light should be the color of the tunnel
        print('Joni ist im Tunnel')
        return 'tunnel'
    elif distance > maxDistance:
        print('högedüge')
        return 'tunnel'
    else:
        print('Ich bin toll')
        return 'tunnel'
    '''




#Function to evaluate how much to steer according to which part of the track the bot is
#@requires everything being initialized the right way
#@ensures motor is not changed

#@returns returns a value in the domain [-70 70] which should be the angle for the wheels (and the raw sensor data)
def getSteeringValue(mode):
    light = storageLight[0]
    distance = storageDistance[0]
    
    if mode == 'light':
        steering = lightToSteering(light)
        change =  mean(storageLight) - light
        
    elif mode == 'tunnel':
        steering = distanceToSteering(distance)
        change = mean(storageDistance) - distance
        
    #TODO
    elif mode == 'transition' or mode == 'transLtoT' or mode == 'transTtoL':
        steering = 1/2 * (lightToSteering(light) + distanceToSteering(distance))
        change = 0

    '''
    changeFactor = 1.5
    expectedValue = steering + changeFactor * change
    if expectedValue <= 100:
        if expectedValue >= -100:
            steering = expectedValue
    '''
    
    #print('Mode: ', mode)
    #print("change" + str(change))

    '''
    wait(3000)
    print('Mode: ', mode)
    print('Distance: ',distance)
    print('Light: ',light)
    print('Change: ', change)
    print('Steer: ', steering)
    '''
    print(light,'uu',steering)
    return steering, mode
    
 #Meassures light and distance
 #Writes them in the first entry of storageDistance and storageLight respectivly
def observe():
    light = lightSensor.reflection()

    #Light signal gets filtered, but after some investigation I think this step is not really necessary
    rawDistance = distanceSensor.distance()
    shift(distanceFilter, rawDistance)
    distance = filter(distanceFilter)


    shift(storageLight, light)
    shift(storageDistance, distance)
    

###########################################################
###########    M A I N     P R O G R A M     ##############
###########################################################

light = lightSensor.reflection()
distance = distanceSensor.distance()
mode = 'light'
for i in range(5):
    distanceFilter[i] = distance
    


while True:
    
    observe()
    mode = getMode(mode)

    
    steeringVal, mode = getSteeringValue(mode)

    driveDifferential(motorLeft, motorRight, 200, steeringVal)

    steerMotor.run_target(600, steeringVal)
    
    #try steerMotor.run_angle -angleError and change getSteeringValue
    #rot = steerMotor.angle()
    #wait(100)

#### TO DO ####

# Ultraschall Fehlerhafte Messungen Filtern



'''
GENERAL INFORMATION 

If you want to understand the code it may be useful to understand, that I always change global variables in functions. That is ugly and shouldn't
be done but it was the most easiest way and it's working.

For example: observe() gets meassures light and distance and then add it to the storage

'''