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
    pygame.mixer.music.play()
    
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
set_volume(0.4)
play()


