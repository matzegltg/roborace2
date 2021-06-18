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

def driveForward(motorLeft, motorRight, speed):
    motorLeft.run(-speed)
    motorRight.run(-speed)


def driveDifferential(motorLeft, motorRight,  speed, steering):
    differential = speed/(maxRot * 2) * steering #Maximum differential 1/4 of speed
    
    motorLeft.run(-speed + differential)
    motorRight.run(-speed - differential)
    


#Function to add value to storage of data
def add(arr, val):
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

    #even shorter
    '''
    val = [0, 140, 190, 400, 500]
    steer = [-90, -30, 0, 40, 80]

    for i in range(1,len(val)): #Checks if distance is in between some interval (can't be <0)
        if distance < val[i]:
            return linear(distance, v[i-1], s[i-1], v[i], s[i-1])
    
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



#Checking for what the current sensor in the map is
#mode: light, tunnel,    # transLtoD, transDtoL
def getMode(light, distance, oldMode):
    #Cyclic method
    if oldMode == 'light':
        if distance < maxDistance:
            return 'transLtoD'
    elif oldMode == 'transLtoD':
        if light > maxLight:
            return 'tunnel'
    elif oldMode == 'tunnel':
        if light < maxLight:
            return 'transDtoL'
    elif oldMode == 'transDtoL':
        if distance > maxDistance:
            return 'light'
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
def getSteeringValue(rot, storageLight, oldMode, distanceFilter, storageDistance):
    steering = 0
    light = lightSensor.reflection()
    rawDistance = distanceSensor.distance()

    #Filter the signal
    add(distanceFilter, rawDistance)
    distance = filterDistance(distanceFilter)
    
    
    mode = getMode(light,distance, oldMode)


    if mode == 'light':
        steering = lightToSteering(light)

        storageLight = add(storageLight, light)
        change =  mean(storageLight) - light
        
    elif mode == 'tunnel':
        steering = distanceToSteering(distance)
        
        storageDistance = add(storageDistance, distance)
        change = mean(storageDistance) - distance
        
    #TODO
    elif mode == 'transition' or mode == 'transLtoD' or mode == 'transDtoL':
        
        steering = 1/2 * (lightToSteering(light) + distanceToSteering(distance))
        change = 0

    '''
    changeFactor = 1.5
    expectedValue = steering + changeFactor * change
    if expectedValue <= 100:
        if expectedValue >= -100:
            steering = expectedValue
    '''
    
    print('Mode: ', mode)
    print("change" + str(change))

    '''
    wait(3000)
    print('Mode: ', mode)
    print('Distance: ',distance)
    print('Light: ',light)
    print('Change: ', change)
    print('Steer: ', steering)
    '''

    return steering, mode
    
 
    

###########################################################
###########    M A I N     P R O G R A M     ##############
###########################################################

driveForward(motorLeft, motorRight, 200)

light = lightSensor.reflection()
distance = distanceSensor.distance()
mode = 'light'
for i in range(5):
    distanceFilter[i] = distance
    


while True:
    rot = steerMotor.angle()
    
    
    steeringVal, mode = getSteeringValue(rot, storageLight, mode, distanceFilter, storageDistance)
    
    driveDifferential(motorLeft, motorRight, 100, steeringVal)

    steerMotor.run_target(600, steeringVal)
    #try steerMotor.run_angle -angleError and change getSteeringValue
    #wait(100)

#### TO DO ####

# Ultraschall Fehlerhafte Messungen Filtern