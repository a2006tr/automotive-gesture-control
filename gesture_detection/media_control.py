import subprocess
import platform

piCheck = platform.system() == "Linux"

if piCheck:
    from bluetooth_hid import startBluetooth, sendMediaControl
    from bluetooth_hid import nextTrackCode, previousTrackCode, volumeUpCode, volumeDownCode, playPauseCode
    startBluetooth()

def next_track():
    if piCheck:
        sendMediaControl(nextTrackCode)
    else:
        subprocess.run(['osascript', '-e', 'tell application "Spotify" to next track'])

def previous_track():
    if piCheck:
        sendMediaControl(previousTrackCode)
    else:
        subprocess.run(['osascript', '-e', 'tell application "Spotify" to previous track'])

def volume_up():
    if piCheck:
        sendMediaControl(volumeUpCode)
    else:
        subprocess.Popen(['osascript', '-e', 'tell application "Spotify" to set sound volume to (sound volume + 5)'])

def volume_down():
    if piCheck:
        sendMediaControl(volumeDownCode)
    else:
        subprocess.Popen(['osascript', '-e', 'tell application "Spotify" to set sound volume to (sound volume - 2)'])

def playPause():
    if piCheck:
        sendMediaControl(playPauseCode)
    else:
        subprocess.Popen(['osascript', '-e', 'tell application "Spotify" to playpause'])