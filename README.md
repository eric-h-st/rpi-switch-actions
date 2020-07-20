# Custom actions (shutdown/reboot/your own other action) on GPIO singal (button) for Raspberry Pi (*hold*, *click* and *double-click*)

A very simple systemd service for Raspberry Pi that supports a configurable software-controlled hardware button, allowing to perform different actions for different hold times of the button, for click and double-click events.

## Use

Default behaviour in response to button activity is:

* Upon short click of the button: the HDMI (TV) will turn off
* Upon short double-click of the button: the HDMI (TV) will turn on
* Button held down for more than six seconds and then released: Raspberry Pi will *reset*, after playing a short chime ('reset.wav')
* Button held down for more than nine seconds and then released: Raspberry Pi will *shut down*, after playing a short chime ('shutdown.wav')
* Beep sound will be played every second the button is held ('click.wav'), until the highest defined limit is reached

By default, the software assumes the switch is connected to pin [BCM 27](https://pinout.xyz/pinout/pin13_gpio27#).

All of the above is configurable by changing the 'config.json' file.

### Configuration
The default configuration supports the above, but everything is configurable. 
```javascript
{
        "hardwareBCMPin": 27, 
        "clickAction": "/usr/bin/tvservice -o" , // optional. The default action is- Turn TV off
        "doubleClickAction": "/usr/bin/tvservice -p;chvt 6;chvt 7", // optional. The default action is- Turn TV back on
        "timedActions": [
                {
                        "name": "Reset RPI", // informational only. unused
                        "elapsedSeconds": 6,
                        "sound": "reset.wav", // optional
                        "action": "/sbin/reboot"
                },
                {
                        "name": "Shutdown RPI", // informational only. unused
                        "elapsedSeconds": 9,
                        "sound": "shutdown.wav", // optional
                        "action": "/sbin/poweroff"
                }
        ],
        "clickSound": "click.wav" // optional 
}
```
## Requirements

### Hardware

* A Raspberry Pi (tested on a model 2B, 3B and Zero, and on a model B after minor software modification)

* A normally open, momentary contact button. I use surplus ATX power
  buttons (as used on desktop PCs), as they're cheap and come with a
  handy set of wires and header connectors. Virtually any button will
  do the job, though. Just make sure it's normally open (push to close).

### Software

* A Debian-based operating system that uses systemd (tested on Jessie and Stretch)
  
* the `python3-gpiozero` package to provide [GPIO
  Zero](https://gpiozero.readthedocs.io/en/stable/) (tested on version 1.4.0)

## Installation

### Hardware

#### 40-pin GPIO connector (B+, 2B, 3B, Zero)

Connect the button between GPIO 27 and GND. If you use an ATX power
button and a Raspberry Pi with a 40-pin GPIO header, connect it across
the seventh column from the left:

                -
    · · · · · ·|·|· · · · · · · · · · · · · 
    · · · · · ·|·|· · · · · · · · · · · · · 
                -

This shorts GPIO 27 (physical pin 13) to ground (physical pin 14) when
the button is pressed.

#### 26-pin GPIO connector (models B and A only)

GPIO 27 is not exposed on the original Raspberry Pi header, so [GPIO 17](https://pinout.xyz/pinout/pin11_gpio17#) is a reasonable option. If you use an ATX power button and a Raspberry Pi with a 26-pin GPIO header, connect it across the fifth and sixth columns of the second row:

    . . . . ._. . . . . . . .
    . . . .|. .|. . . . . . .
             -
You will also need to change [line 7 of shutdown_button.py](https://github.com/scruss/shutdown_button/blob/master/shutdown_button.py#L7) to read:

    use_button=17

### Software

`git clone https://github.com/eric-h-st/rpi-switch-actions rpi-switch-actions`

The software is installed with the following commands:

    sudo apt install python3-gpiozero
    cd rpi-switch-actions
    sh install.sh

You can use 'sh install.sh' to re-install, if changes are made, such as- replacing sound files or for configuration changes

## Troubleshooting

Enabling the service should produce output very similar to:

    Created symlink /etc/systemd/system/multi-user.target.wants/shutdown_button.service → /etc/systemd/system/shutdown_button.service.

You can check the status of the program at any time with the command:
	
    systemctl status shutdown_button.service

This should produce output similar to:
	
    ● shutdown_button.service - GPIO shutdown button
       Loaded: loaded (/etc/systemd/system/shutdown_button.service; enabled; vendor 
       Active: active (running) since Sat 2017-10-21 11:20:56 EDT; 27s ago
     Main PID: 3157 (python3)
       CGroup: /system.slice/shutdown_button.service
               └─3157 /usr/bin/python3 /usr/local/bin/shutdown_button.py

    Oct 21 11:20:56 naan systemd[1]: Started GPIO shutdown button.

If you're seeing anything *other* than **Active: active (running)**,
it's not working. Does the Python script have the right permissions?
Is it in the right place? If you modified the script, did you check it
for syntax errors? If you're using a model A or B with a 26-pin GPIO connector, did you make the modifications in the Python script to use GPIO 17 instead of 27?

The output from `dmesg` will show you any error messages generated by
the service.

Also, for a more coherent report, you could go to the system logs in `/var/log/syslog`

## Modifications

If you use a HAT/pHAT/Bonnet/etc. with your Raspberry Pi, check
[pinout.xyz](https://pinout.xyz/) to see if it uses BCM 27. If you do
need to change the pin, best to pick one that doesn't have a useful
system service like serial I/O or SPI. If you're using an ATX button
with a two pin connector, make sure you choose a pin physically
adjacent to a ground pin.

## Notes

You should not need to reboot to enable the service. One machine of
mine — a Raspberry Pi Zero running Raspbian Stretch — did need a
reboot before the button worked.

The reboot code is based on the [Shutdown
button](https://gpiozero.readthedocs.io/en/stable/recipes.html#shutdown-button)
example from the GPIO Zero documentation.

This is not the only combined shutdown/reset button project to use
GPIO Zero. [gilyes/pi-shutdown](https://github.com/gilyes/pi-shutdown)
also does so, but pre-dates the implementation of the various hold
time functions in GPIO Zero.

GPIO 27 was used, as it's broken out onto a physical button on the Adafruit [PiTFT+](http://adafru.it/2423) display I own.

### Connector Pinouts

From GPIO Zero's `pinout` command

#### 40 pin

       3V3  (1) (2)  5V    
     GPIO2  (3) (4)  5V    
     GPIO3  (5) (6)  GND   
     GPIO4  (7) (8)  GPIO14
       GND  (9) (10) GPIO15
    GPIO17 (11) (12) GPIO18
    GPIO27 (13) (14) GND   
    GPIO22 (15) (16) GPIO23
       3V3 (17) (18) GPIO24
    GPIO10 (19) (20) GND   
     GPIO9 (21) (22) GPIO25
    GPIO11 (23) (24) GPIO8 
       GND (25) (26) GPIO7 
     GPIO0 (27) (28) GPIO1 
     GPIO5 (29) (30) GND   
     GPIO6 (31) (32) GPIO12
    GPIO13 (33) (34) GND   
    GPIO19 (35) (36) GPIO16
    GPIO26 (37) (38) GPIO20
       GND (39) (40) GPIO21
    
#### 26 pin

       3V3  (1) (2)  5V    
     GPIO0  (3) (4)  5V    
     GPIO1  (5) (6)  GND   
     GPIO4  (7) (8)  GPIO14
       GND  (9) (10) GPIO15
    GPIO17 (11) (12) GPIO18
    GPIO21 (13) (14) GND   
    GPIO22 (15) (16) GPIO23
       3V3 (17) (18) GPIO24
    GPIO10 (19) (20) GND   
     GPIO9 (21) (22) GPIO25
    GPIO11 (23) (24) GPIO8 
       GND (25) (26) GPIO7 
    
## Authors

Eric H. 

This project is based on a project by: Stewart C. Russell, with permission — https://github.com/scruss/shutdown_button 


