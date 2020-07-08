#!/usr/bin/python3
# -*- coding: utf-8 -*-
# example gpiozero code that could be used to have a reboot
#  and a shutdown function on one GPIO button
# scruss - 2017-10

use_button=27                       # lowest button on PiTFT+

import os
from gpiozero import Button
from signal import pause
from subprocess import check_call
from pygame import mixer
import json

print('Started')
path=os.path.dirname(os.path.realpath(__file__))

print('Reading config');
with open('config.json', 'r') as configFile:
    config = json.load(configFile);
print('accessing actions')
actions = config['actions']
if (actions is None):
    exit('Error reading config: actions is mandatory')

actions.sort(key=lambda x: x.get('elapsedSeconds'))

mixer.init()

if (config['clickSound'] is not None):
    clickSound = mixer.Sound(config['clickSound'])
for action in actions:
    if (action['sound'] is not None):
        action['soundModule'] = mixer.Sound(action['sound'])
    else:
        action['soundModule'] = None

held_for=0.0
resetAt=5
shutdownAt=10
global selectedAction 
selectedAction = None

def rls():
        global selectedAction
        if (selectedAction is not None):
            os.system(selectedAction)
        selectedAction = None

def hld():
        global selectedAction
        # callback for when button is held
        #  is called every hold_time seconds
        held_for = button.held_time + button.hold_time

        actionFound = False
        for action in actions:
            actionElapsedSeconds = action["elapsedSeconds"]
            if (held_for > actionElapsedSeconds  and held_for < actionElapsedSeconds  + 1):
                if (action["soundModule"] is not None):
                    action["soundModule"].play(0,900)
                if (action["action"] is not None):
                    selectedAction = action["action"]
                    actionFound = True
        if (not actionFound and clickSound is not None):
            clickSound.play(0,900)

button=Button(use_button, hold_time=1.0, hold_repeat=True)
button.when_held = hld
button.when_released = rls

pause() # wait forever
