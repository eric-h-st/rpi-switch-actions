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
selectedAction = None
clickMode = 0
timer = None
lastClickSoundTime = 0

def rls():
        global selectedAction
        global clickMode
        global timer
        global lastClickSoundTime

        lastClickSoundTime = 0
        if (clickMode == 0):
            if (selectedAction is not None):
                print("Performing: ", action["name"])
                os.system(selectedAction)
            selectedAction = None
        elif (clickMode == 1):
            if (timer is not None):
                clickMode = 2
            else:
                print("Starting click timer")
                timer=threading.Timer(0.250, actOnClicks)
                timer.start()

def actOnClicks():
       global timer
       timer.cancel()
       timer = None
       print("Click timer up, clickMode=", clickMode)
       if (clickMode == 1 and config["clickAction"] is not None):
           os.system(config["clickAction"])
       elif (clickMode == 2 and config["doubleClickAction"] is not None):
           os.system(config["doubleClickAction"])

def hld():
        global selectedAction
        global clickMode
        global lastClickSoundTime
        # callback for when button is held
        #  is called every hold_time seconds
        held_for = button.held_time + button.hold_time

        if (held_for > 0.05 and held_for < 0.250):
            clickMode=1
        else:
            clickMode = 0
            actionFound = False
            for action in actions:
                actionElapsedSeconds = action["elapsedSeconds"]
                if (held_for > actionElapsedSeconds  and held_for < actionElapsedSeconds  + 1):
                    if (action["soundModule"] is not None):
                        action["soundModule"].play(0,900)
                    if (action["action"] is not None):
                        selectedAction = action["action"]
                        actionFound = True
            if (held_for > lastClickSoundTime + 1):
                lastClickSoundTime = math.floor(held_for)
                print(lastClickSoundTime, held_for)
                if (not actionFound and clickSound is not None):
                    print("Beep")
                    clickSound.play(0,900)

button=Button(hardwareBCMPin, hold_time=0.050, hold_repeat=True)
button.when_held = hld
button.when_released = rls

pause() # wait forever
