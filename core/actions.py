import os
import time
import pygame
from mutagen.mp3 import MP3

pygame.mixer.init()
playlist = []
current_index = -1

# Temps en ms où la lecture a été mise en pause (ou position de départ)
last_seek_position = 0

# Timestamp (en secondes) du moment où la musique a été lancée/reprise
play_start_time = None

def load_playlist_from_folder(folder_path):
    global playlist, current_index
    playlist.clear()
    current_index = -1
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.mp3', '.wav', '.ogg')):
            playlist.append(os.path.join(folder_path, filename))

def get_current_index():
    global current_index
    return current_index

def set_current_index(index):
    global current_index, last_seek_position, play_start_time
    if 0 <= index < len(playlist):
        current_index = index
        last_seek_position = 0
        play_start_time = None

def load_track_by_index(index):
    global current_index, last_seek_position, play_start_time
    if 0 <= index < len(playlist):
        current_index = index
        last_seek_position = 0
        play_start_time = None
        pygame.mixer.music.load(playlist[index])

def play_music():
    global play_start_time
    if current_index == -1 and len(playlist) > 0:
        load_track_by_index(0)
    pygame.mixer.music.play(start=last_seek_position / 1000)
    play_start_time = time.time()

def pause_music():
    global last_seek_position, play_start_time
    if play_start_time is not None:
        elapsed_ms = int((time.time() - play_start_time) * 1000)
        last_seek_position += elapsed_ms
        play_start_time = None
    pygame.mixer.music.pause()

def loop_music():
    global play_start_time
    if current_index == -1 and len(playlist) > 0:
        load_track_by_index(0)
    pygame.mixer.music.play(loops=-1, start=last_seek_position / 1000)
    play_start_time = time.time()

def stop_music():
    global last_seek_position, play_start_time
    pygame.mixer.music.stop()
    last_seek_position = 0
    play_start_time = None

def skip_track():
    global current_index
    if not playlist:
        return
    new_index = (current_index + 1) % len(playlist)
    set_current_index(new_index)
    load_track_by_index(new_index)
    play_music()

def rewind_track():
    global last_seek_position, play_start_time
    last_seek_position = 0
    play_start_time = time.time()
    pygame.mixer.music.play(start=0)

def set_volume(vol):
    pygame.mixer.music.set_volume(vol)

def get_current_position_ms():
    global last_seek_position, play_start_time
    if play_start_time is None:
        return last_seek_position
    elapsed_ms = int((time.time() - play_start_time) * 1000)
    return last_seek_position + elapsed_ms

def get_current_track_duration_ms():
    if current_index == -1 or not playlist:
        return 0
    try:
        audio = MP3(playlist[current_index])
        return int(audio.info.length * 1000)
    except Exception:
        return 0

def seek_to_position(ms):
    global last_seek_position, play_start_time
    if current_index == -1:
        return
    last_seek_position = ms
    play_start_time = time.time()
    pygame.mixer.music.load(playlist[current_index])
    pygame.mixer.music.play(start=ms / 1000)

def get_current_track_name():
    if 0 <= current_index < len(playlist):
        return os.path.basename(playlist[current_index])
    return ""
