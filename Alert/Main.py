import pygame
import sys
import pynput
import a2s
import math
import datetime
import winsound
import os
import time
import threading
from queue import Queue
import win32gui
import win32con
import math
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (1660,10)
# Game initialization
pygame.init()
pygame.mixer.init()



window = pygame.display.set_mode((8*30, 4*30), pygame.NOFRAME, 32)
pygame.display.set_caption('Alert')
pygame.font.init()

Arial = pygame.font.SysFont('Arial', 30)
clock = pygame.time.Clock()

ToDraw = []  # Store text to be drawn
global retries
timemode = 0
retries = 0

# Shared queue to communicate between threads
data_queue = Queue()
def beep():
    pygame.mixer.Sound.play(pygame.mixer.Sound("beep.mp3"))
    return

def Render(*args):
    for i in args:
        window.blit(i, (0, args.index(i) * 30))  # Draw text at different y positions based on the index
    return

def GetWstr(TimeOut: int = 5, Address: tuple = ("79.127.217.197", 22912), retries=0):
    try:
        info : a2s.SourceInfo = a2s.info(Address, timeout=TimeOut)
        players = a2s.players(Address, timeout=TimeOut)
        duration = 0

        for player in players:
            duration = max(duration, player.duration)
        os.system('cls')
        playercount = info.player_count
        if info.map_name == "":
            info.map_name = "DILL IS ACTIVE"
        maxplayers = info.max_players
        password = info.password_protected
        if timemode == 0:
            Ttime = f"time left={str(datetime.timedelta(seconds=1800 - math.floor(duration)))}"
        else:
            now = datetime.datetime.now()
            next_half_hour = (now + datetime.timedelta(minutes=60 - now.minute % 60)).replace(second=0, microsecond=0)
            Ttime = f"time left={str(next_half_hour - now.replace(microsecond=0))}"
        wstr = f"playercount={str(playercount)}/{str(maxplayers)}\nmap={info.map_name}\npassword={str(password)}\n{Ttime}"
        retries = 0

        if playercount == 0:
            pass
    except Exception as e:
        wstr = f"Error: {e} ({retries})"
        retries += 1
    return [wstr, retries]

def DrawText(str):
    str = str.split("\n")
    ToDraw.clear()  # Clear the previous text before drawing the new one
    for line in str:
        # Append each line as a new surface to ToDraw
        ToDraw.append(Arial.render(line, True, (255, 255, 255)))

def update_network_data():
    global retries
    while True:
        # Run the blocking network function in the background
        wstr, retries = GetWstr(retries=retries)
        data_queue.put((wstr, retries))  # Send the result to the main thread

# Start a background thread for network updates
network_thread = threading.Thread(target=update_network_data, daemon=True)
network_thread.start()
# Game loop
def game_loop():
    win32gui.SetWindowPos(pygame.display.get_wm_info()['window'], win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
    global retries
    while True:
        global timemode
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    timemode = int(not timemode)

        # Check if there is any new data from the background thread
        if not data_queue.empty():
            wstr, retries = data_queue.get()
            with open("retry.txt", "w") as f:
                f.write(wstr)
            print(wstr)
            DrawText(wstr)  # Update the text to be drawn

        # Game code here
        window.fill((0, 0, 0))  # Clear the screen once
        Render(*ToDraw)  # Draw the updated text
        pygame.display.update()
        clock.tick(60)

# Run the game loop
if __name__ == "__main__":
    game_loop()
