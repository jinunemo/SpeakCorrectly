import pygame

def play_beep_sound(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue
