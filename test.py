from vlc import State, Media, MediaPlayer
import time

a = MediaPlayer()

a.set_media(Media(r"C:\Users\Microsoft\Music\1.mp3"))
a.set_rate(2)
a.play()

while a.get_state() != State(6):
    time.sleep(.5)
