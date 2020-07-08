#!/usr/bin/python3
# eric-h-st - 2020-07
# scruss - 2017-10

import os
import threading
from gpiozero import Button
from signal import pause
from subprocess import check_call
from pygame import mixer
import json
import math

path=os.path.dirname(os.path.realpath(__file__))

with open(path+'/config.json', 'r') as configFile:
    config = json.load(configFile);

hardwareBCMPin = config["hardwareBCMPin"]
if (hardwareBCMPin is None):
    hardwareBCMPin = 27

actions = config["timedActions"]
if (actions is None):
    exit('Error reading config: actions is mandatory')

actions.sort(key=lambda x: x.get('elapsedSeconds'))

mixer.init()

if (config['clickSound'] is not None):
    clickSound = mixer.Sound(path+"/"+config['clickSound'])
for action in actions:
    if (action['sound'] is not None):
        action['soundModule'] = mixer.Sound(path+"/"+action['sound'])
    else:
        action['soundModule'] = None

global selectedAction
global clickMode
global timer
global lastClickSoundTime
global actionNum

selectedAction = None
clickMode = 0
timer = None
lastClickSoundTime = 0
actionNum = 0

def actOnButtonRelease():
        global selectedAction
        global clickMode
        global timer
        global lastClickSoundTime
        global actionNum

        lastClickSoundTime = 0
        if (clickMode == 0):
            if (selectedAction is not None):
                os.system(selectedAction)
            selectedAction = None
            actionNum = 0
        elif (clickMode == 1):
            if (timer is not None):
                clickMode = 2
            else:
                timer=threading.Timer(0.250, actOnClicks)
                timer.start()

def actOnClicks():
       global timer
       timer.cancel()
       timer = None
       if (clickMode == 1 and config["clickAction"] is not None):
           os.system(config["clickAction"])
       elif (clickMode == 2 and config["doubleClickAction"] is not None):
           os.system(config["doubleClickAction"])

def actOnButtonHold():
        global selectedAction
        global clickMode
        global lastClickSoundTime
        global actionNum

        held_for = button.held_time + button.hold_time

        if (held_for > 0.05 and held_for < 0.250):
            clickMode=1
        else:
            clickMode = 0
            actionFound = False
            if (actionNum == (len(actions))):
                return;

            action = actions[actionNum]
            if (action["elapsedSeconds"] is None):
                actionElapsedSeconds = 99
            else:
                actionElapsedSeconds = action["elapsedSeconds"]

            if (held_for > actionElapsedSeconds):
                if (action["soundModule"] is not None and selectedAction != action["action"]):
                    action["soundModule"].play(0,900)
                if (action["action"] is not None):
                    selectedAction = action["action"]
                    actionFound = True
                actionNum = actionNum + 1
            if (held_for > lastClickSoundTime + 1):
                lastClickSoundTime = math.floor(held_for)
                if (not actionFound and clickSound is not None):
                    clickSound.play(0,900)

button=Button(hardwareBCMPin, hold_time=0.050, hold_repeat=True)
button.when_held = actOnButtonHold
button.when_released = actOnButtonRelease

pause() # wait forever
