#!/usr/bin/python
import os
import sys
import time
from datetime import datetime
import spidev
from sound_log import Logger
from camera import Camera

################### 
#music player
import pygame
from time import sleep

def init():
    pygame.init()
    pygame.mixer.init()

def load(track):
    pygame.mixer.music.load(track)

def unload(track):
    pygame.mixer.music.unload(track)
    
def set_volume(volume):
    pygame.mixer.music.set_volume(volume)

def get_volume(volume):
    pygame.mixer.music.get_volume(volume)
    
def play():
    pygame.mixer.music.play(-1)
    
def stop():
    pygame.mixer.music.stop()
    
def pause():
    pygame.mixer.music.pause()

def unpause():
    pygame.mixer.music.unpause()

def rewind():
    pygame.mixer.music.rewind()

def get_currently_playing():
    pygame.mixer.music.get_busy()



init()
load("music.mp3")
set_volume(0.2)


##################

sys.excepthook = sys.__excepthook__

# Spidev used to connect to and read the sensors
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000
 
def read_channel(channel):
  val = spi.xfer2([1,(8+channel)<<4,0])
  data = ((val[1]&3) << 8) + val[2]
  return data

def get_volts(channel=0):
    v=(read_channel(channel)/1023.0)*3.3
    print("Channel ", channel, " : %.2f V" % v) 
    return v

def is_in_range(v, i):
    # Threshold for every sensor: probably depends on the location 
    # and have to be tested and adjusted
    if i == 0 and v > 1.7 and v < 2.5:
        return True
    #elif i == 0 and v > 0.00:
    #    return True
    else:
       return False
 
# Update local log file
def update_log(logger, start=False, end=False, sensors_active=[]):
    now = datetime.now()
    timestr = now.strftime("%Y-%m-%d %H:%M:%S")
    data = [timestr, start, end] + sensors_active
    logger.log_local(data)




  
if __name__ == "__main__":
    camera = Camera()
    camDirectory = '/media/pi/9A368D3E368D1BFF/camera-records/'
    print(os.getpid())
    status_in_range = False
    playing = False
    paused = False
    is_playing = False
    channel_indices = [0]
    logger = Logger()
    prev_alive_time = datetime.now()
    logger.log_alive()
    while True:
        
        cameraIsRecording = camera.is_recording()
        now = datetime.now()
        diff = (now - prev_alive_time).total_seconds() / 60.0
        # ping alive every 5 mins
        if diff > 5:
            #print('Log alive!', diff)
            logger.log_alive()
            prev_alive_time = now

        # online logging intitated separate from sensor readings, so that if the quota is passed and data accumulated 
        # only locally, the waiting records will be logged as soon as possible whether there is activity going on
        # or not
        logger.log_drive(now)
        sensors_in_range = [is_in_range(get_volts(i), i) for i in channel_indices]
        new_in_range = any(sensors_in_range)


        # Require two consecutive sensor readings before
        # triggering play to prevent random activations
        if new_in_range and status_in_range:
            
            # record start of sound play for logging
            start = True
                
            # if paused resume
            if paused == True:
                unpause()
                paused = False
                is_playing = True
            # otherwise start playing if not already on
            elif is_playing == False:
                play()
                is_playing = True
                paused = False
            else:
                # status is 1 i.e. already playing
                start = False
                
            playing = True
            update_log(logger, start=start, sensors_active=sensors_in_range)
            
            if not cameraIsRecording:
                fileName = datetime.now().strftime("%d-%m-%Y-%H:%M:%S")
                camera.start_recording(fileName, camDirectory)
            
            
        if playing and not new_in_range:
            camera.stop_recording()
            pause()
            paused = True
            playing = False
            update_log(logger, end=True, sensors_active=sensors_in_range)
        status_in_range = new_in_range
        time.sleep(0.4)

