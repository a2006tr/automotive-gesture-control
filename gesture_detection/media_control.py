import subprocess
def next_track():
    subprocess.run(['osascript', '-e', 'tell application "Spotify" to next track'])
def previous_track():
    subprocess.run(['osascript', '-e', 'tell application "Spotify" to previous track'])