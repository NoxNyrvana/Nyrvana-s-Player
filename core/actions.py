import os
import pygame
from mutagen.mp3 import MP3

pygame.mixer.init()
playlist = []
current_index = -1
last_seek_position = 0

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
    """Change l'index global de la piste courante."""
    global current_index
    if 0 <= index < len(playlist):
        current_index = index

def load_track_by_index(index):
    global current_index, last_seek_position
    if 0 <= index < len(playlist):
        current_index = index
        last_seek_position = 0
        pygame.mixer.music.load(playlist[index])

def play_music():
    global last_seek_position
    if current_index == -1 and len(playlist) > 0:
        load_track_by_index(0)
    pygame.mixer.music.play(start=last_seek_position / 1000)

def pause_music():
    pygame.mixer.music.pause()

def stop_music():
    pygame.mixer.music.stop()

def skip_track():
    global current_index, last_seek_position
    if len(playlist) == 0:
        return
    current_index += 1
    if current_index >= len(playlist):
        current_index = 0
    last_seek_position = 0
    load_track_by_index(current_index)
    play_music()

def rewind_track():
    """Remet la piste au début."""
    global last_seek_position
    if current_index == -1:
        return
    last_seek_position = 0
    pygame.mixer.music.play(start=0)

def set_volume(vol):
    pygame.mixer.music.set_volume(vol)

def get_current_position_ms():
    global last_seek_position
    pos = pygame.mixer.music.get_pos()
    if pos == -1:
        return last_seek_position
    return last_seek_position + pos

def get_current_track_duration_ms():
    if current_index == -1 or len(playlist) == 0:
        return 0
    try:
        audio = MP3(playlist[current_index])
        return int(audio.info.length * 1000)
    except:
        return 0

def seek_to_position(ms):
    global last_seek_position
    if current_index == -1:
        return
    last_seek_position = ms
    pygame.mixer.music.load(playlist[current_index])
    pygame.mixer.music.play(start=ms / 1000)

def get_current_track_name():
    if 0 <= current_index < len(playlist):
        return os.path.basename(playlist[current_index])
    return ""
