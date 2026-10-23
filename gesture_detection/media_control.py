import subprocess
def next_track():
    subprocess.run(['osascript', '-e', 'tell application "Spotify" to next track'])
def previous_track():
    subprocess.run(['osascript', '-e', 'tell application "Spotify" to previous track'])
def volume_up():
    subprocess.Popen(['osascript', '-e', 'tell application "Spotify" to set sound volume to (sound volume + 5)'])
def volume_down():
    subprocess.Popen(['osascript', '-e', 'tell application "Spotify" to set sound volume to (sound volume - 2)'])