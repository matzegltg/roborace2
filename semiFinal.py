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


'''
____________________________________________________________________________________________________
GENERAL INFORMATION 

This is the code for a self driving car - just worse

If you want to understand the code it may be useful to understand, that I always change global variables 
in functions. That is ugly and shouldn't be done but it was the most easiest way and it's working.

For example: observe() meassures light and distance and then add it to the storage
____________________________________________________________________________________________________
Important variables

maxDistance - if out tunnel
maxLight - if in tunnel

steering function interpolation values

____________________________________________________________________________________________________
TO DO

Ultraschall Fehlerhafte Messungen Filtern
optimize Factor of change

Remove Beep when changing mode
Remove tests
____________________________________________________________________________________________________
'''
###########################################################
###### Fun                           ######################    
###########################################################

ev3 = EV3Brick()
ev3.speaker.say('Lets go 1.FC Fleischkäsweckle')
notes = ['C4/4', 'E4/4', 'A4/8', 'G4/2', 'E5/8','D5/2'] #Robo Melody
ev3.speaker.play_notes(notes, tempo=120)






###########################################################
###### Initialising the Hardware     ######################    
###########################################################


#Motors
motorLeft = Motor(Port.C)
motorRight = Motor(Port.D)
steerMotor = Motor(Port.B)

#Sensors
distanceSensor = UltrasonicSensor(Port.S3)
lightSensor = ColorSensor(Port.S2)


#Defining some expected constants
normalBrightness = 13 #lightSensor.reflection() #Either by meassuring in a nother helper function or just hard code this magic numbers
normalDistance = 190

maxLight = 60
maxDistance = 300

storageLight = []
storageDistance = []
distanceFilter = [0, 0, 0, 0, 0]
for i in range(25):
    storageLight.append(normalBrightness)
    storageDistance.append(normalDistance)
    

#################
# T E S T I N G #
#################
stopTrigger = TouchSensor(Port.S4) #right
changeMode = TouchSensor(Port.S1) # left
testLV = []
testLC = []
testDV = []
testDC = []
testSteering = []




###########################################################    
###### Defining some helper functions     #################
###########################################################

def driveForward(speed):
    motorLeft.run(-speed)
    motorRight.run(-speed)

#Evaluates a linear function defined by two given points
def linear(x, x0, y0, x1, y1):
    return (y1 - y0)/(x1 - x0) * (x - x0) + y0


##### A R R A Y   F U N C T I O N S #####

#Function to shift value to storage of data
def shift(arr, val):
    for i in range(1,len(arr)):
        arr[-i] = arr[-(i+1)] #second last is mapped to last ...
    arr[0] = val

def mean(arr):
    return sum(arr)/len(arr)
        
def filter(arr):
    return (sum(arr) - max(arr))/len(arr)





##### S T E E R   F U N C T I O N S #####

#Reminder for Steering:
    #Left - pos.  & Right - neg.
    #Values between [-90 100]


#Function is a semi linear function - see plots in the file for information
    #lightToSteeringPlot.png
    #distanceToSteeringPlot.png
    
    
    
#Reminder for Light Sensor:
    #High - bright  &  Low - dark
    #values in [0 40]

    #If dark we steer left (0 -> 100) and vice versa (40 -> -90)
def lightToSteering(light):
    
    
    val =   [  0,  10,  13,  17,  25,  40]
    steer = [90,  30,   0, -40, -75, -90]

    if light < 0:
        return steer[0]

    for i in range(1,len(val)): #Checks if distance is in between some interval of val (can't be <0)
        if light < val[i]:
            return linear(light, val[i-1], steer[i-1], val[i], steer[i])
    
    return steer[-1] #This is the last element 


#Reminder for Distance Sensor:
    #Distance in mm and obviously the more the further away

    #If close we drive right (50 (mm) -> -70)
def distanceToSteering(distance):
    ### Input Data ###
    #valD =   [  0, 140, 190, 250, 400, 500]
    #steer = [-90, -90, -20,  20,  40,  70]
    valD = [  0, 150, 450, 600]
    steer= [-90, -90,  50,  70]

    if distance < 0:
        return steer[0]

    for i in range(1,len(valD)): #Checks if distance is in between some interval
        if distance < valD[i]:
            return linear(distance, valD[i-1], steer[i-1], valD[i], steer[i])
    
    return steer[-1] #This is the last element 
    


#TODO
def changeToSteeringLight():
    pass

def changeToSteeringDist():
    pass



##### M O D E #####

#Checking for what the current sensor in the map is
#mode: light, tunnel,    # transLtoD, transDtoL
def getMode(oldMode):
    #Cyclic method
    light = storageLight[0]
    distance = storageDistance[0]
    if oldMode == 'light':
        if distance < maxDistance:
            ev3.speaker.beep(200)
            return 'transLtoT'

    elif oldMode == 'transLtoT':
        if light > maxLight:
            ev3.speaker.beep(400)
            return 'tunnel'

    elif oldMode == 'tunnel':
        if light < maxLight:
            ev3.speaker.beep(800)
            return 'transTtoL'
            
    elif oldMode == 'transTtoL':
        if distance > maxDistance:
            ev3.speaker.beep(1600)
            return 'light'

    return oldMode


##### S T E E R I N G #####

#Function to evaluate how much to steer according to which part of the track the bot is
#@returns returns a value in the domain [-70 70] which should be the angle for the wheels (and the raw sensor data)
def getSteeringValue(mode):
    light = storageLight[0] #current measurement 
    distance = storageDistance[0]
    


    if mode == 'light':
        change =  light - mean(storageLight)


        #We interpolate the curvature of the car and pretend it is already further
        fac = 1
        inter = light + fac * change
        steering = lightToSteering(inter)
        
    elif mode == 'tunnel':
        change = distance - mean(storageDistance)
        


        fac1 = 5
        inter = distance + fac1 * change
        steering = distanceToSteering(inter)
        
        
        
    #TODO
    elif mode == 'transLtoT' or mode == 'transTtoL':
        steering = 1/2 * (lightToSteering(light) + distanceToSteering(distance))
        change = 0



    ##################################
    # R E M O V E   
    #Storing Values to gain information

    
    testLV.append(light)
    testDV.append(distance)
    testSteering.append(steering)
    if mode =='tunnel':
        testDC.append(change)
        testLC.append(0)
    else:
        testDC.append(0)
        testLC.append(change)
    
    ###################################



    return steering
    



##### S E N S O R S #####

 #Meassures light and distance
 #Writes them in the first entry of storageDistance and storageLight respectivly
def observe():
    light = lightSensor.reflection()

    
    distance =distanceSensor.distance()

    shift(storageLight, light)
    shift(storageDistance, distance)
    







###########################################################
###########    M A I N     P R O G R A M     ##############
###########################################################

driveForward(300) #Speed

mode = 'light' #Starting Position



while True:
    observe()

    #mode = getMode(mode)
    
    steeringVal = getSteeringValue(mode)

    steerMotor.run_target(600, steeringVal)

    if(stopTrigger.pressed()):
        driveForward(0)
        ev3.speaker.say('Programm ended')
        break

    if(changeMode.pressed()):
        ev3.speaker.beep()
        if mode == 'light':
            mode = 'tunnel'
        else:
            mode = 'light'

    
print('testLV = ',testLV, ';')
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
print('testLC = ', testLC, ';')
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
print('testDV = ',testDV, ';')
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
print('testDC = ',testDC,';')
print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
print('testSteering = ',testSteering,';')

###################
####Other Ideas####
###################


# try steerMotor.run_angle -angleError and change getSteeringValue
#rot = steerMotor.angle()
#wait(100)

#Filtering
#Light signal gets filtered, but after some investigation I think this step is not really necessary
'''
rawDistance = distanceSensor.distance()
shift(distanceFilter, rawDistance)
distance = filter(distanceFilter)
print(distanceFilter)
'''

'''
for i in range(5):
    distanceFilter[i] = distance
''' 



#Get mode
'''
    #Smaller but the change section goes nuts
    light = storageLight[0]
    distance = storageDistance[0]
    if oldMode == 'light':
        if distance < maxDistance:
            ev3.speaker.beep(200)
            return 'tunnel'
    elif oldMode == 'tunnel':
        if light < maxLight:
            ev3.speaker.beep(800)
            return 'light'
    return oldMode
    '''