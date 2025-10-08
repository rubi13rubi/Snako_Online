#Input manager and stuff
#___________________________________________________________

global isWindows
isWindows = False
try:
    from win32api import STD_INPUT_HANDLE
    from win32console import GetStdHandle, KEY_EVENT, ENABLE_ECHO_INPUT, ENABLE_LINE_INPUT, ENABLE_PROCESSED_INPUT
    isWindows = True
except ImportError as e:
    import sys
    import os
    import termios


class KeyPoller():
    def __enter__(self):
        global isWindows
        if isWindows:
            self.readHandle = GetStdHandle(STD_INPUT_HANDLE)
            self.readHandle.SetConsoleMode(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_PROCESSED_INPUT)

            self.curEventLength = 0
            self.curKeysLength = 0

            self.capturedChars = []
        else:
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # Set stdin to non-blocking mode
            self.old_flags = os.O_NONBLOCK
            os.set_blocking(self.fd, False)

        return self

    def __exit__(self, type, value, traceback):
        global isWindows
        if isWindows:
            pass
        else:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)
            os.set_blocking(self.fd, True)  # Restore blocking mode

    def poll(self):
        global isWindows
        if isWindows:
            if not len(self.capturedChars) == 0:
                return self.capturedChars.pop(0)

            eventsPeek = self.readHandle.PeekConsoleInput(10000)

            if len(eventsPeek) == 0:
                return None

            if not len(eventsPeek) == self.curEventLength:
                for curEvent in eventsPeek[self.curEventLength:]:
                    if curEvent.EventType == KEY_EVENT:
                        if not curEvent.KeyDown:
                            pass
                        else:
                            curChar = str(curEvent.VirtualKeyCode)
                            self.capturedChars.append(curChar)
                self.curEventLength = len(eventsPeek)

            if not len(self.capturedChars) == 0:
                return self.capturedChars.pop(0)
            else:
                return None
        else:
            try:
                # Read a single character from stdin
                c = sys.stdin.read(1)
                return c if c else None
            except IOError:
                return None
#___________________________________________________________
#Snake class and fragments
#___________________________________________________________
class Snake:
    def __init__(self,x, y):
        self.length = 2
        self.head = SnakeFragment(x,y,0)
        self.tail = SnakeFragment(x,y-1,0)
        self.head.setNext(self.tail)
        self.tail.setPrev(self.head)
        self.disabled = False
        self.haschangeddirection = False
    def getheadxy(self):
        return (self.head.x,self.head.y)
    def gettailxy(self):
        return (self.tail.x,self.tail.y)
    def getlength(self):
        return self.length
    def setdirection(self,direction):
        if not self.haschangeddirection:
            self.haschangeddirection = True
            self.head.setdirection(direction)
    def move(self, mapx, mapy, mapcollisions):
        self.haschangeddirection = False
        return self.head.move(mapx,mapy,mapcollisions)
    def checkcollision(self, snakelist): #returns the index of the snake that the head collided with, or -1 if no collision
        for snake in snakelist:
            if (snake != self and self.head.checkcollision(snake.head.x,snake.head.y)) or (snake == self and self.head.next.checkcollision(self.head.x,self.head.y)):
                return snakelist.index(snake)
        return -1
    def increaselength(self):
        self.length += 1
        if self.tail.direction == 0:
            newtailx = self.tail.x
            newtaily = self.tail.y - 1
        elif self.tail.direction == 1:
            newtailx = self.tail.x - 1
            newtaily = self.tail.y
        elif self.tail.direction == 2:
            newtailx = self.tail.x
            newtaily = self.tail.y + 1
        else:
            newtailx = self.tail.x + 1
            newtaily = self.tail.y
        newtail = SnakeFragment(newtailx,newtaily,self.tail.direction)
        newtail.setPrev(self.tail)
        self.tail.setNext(newtail)
        self.tail = newtail
    def getpositions(self):
        if self.disabled: return []
        return self.head.getpositions()
    def disable(self):
        self.disabled = True
    def isdisabled(self):
        return self.disabled

class SnakeFragment:
    def __init__(self,x,y,direction):
        self.x = x
        self.y = y
        self.next = None
        self.prev = None
        self.direction = direction
    def setNext(self,next):
        self.next = next
    def setPrev(self,prev):
        self.prev = prev
    def setdirection(self,direction):
        self.direction = direction
    def move(self, mapx, mapy, mapcollisions): #moves the snake, returns true if the fragment exited the map and reposistions it on the other side if mapcollisions is false
        if self.direction == 0:
            self.y += 1
            if self.y >= mapy:
                if mapcollisions:
                    return True
                else:
                    self.y = 0
        elif self.direction == 1:
            self.x += 1
            if self.x >= mapx:
                if mapcollisions:
                    return True
                else:
                    self.x = 0
        elif self.direction == 2:
            self.y -= 1
            if self.y < 0:
                if mapcollisions:
                    return True
                else:
                    self.y = mapy - 1
        elif self.direction == 3:
            self.x -= 1
            if self.x < 0:
                if mapcollisions:
                    return True
                else:
                    self.x = mapx - 1
        if self.next != None:
            self.next.move(mapx,mapy,mapcollisions)
            self.next.setdirection(self.direction)
    def getpositions(self):
        if self.next != None:
            return [(self.x, self.y)] + self.next.getpositions()
        else:
            return [(self.x, self.y)]
    def checkcollision(self, x, y):
        if self.next != None:
            if self.next.x == x and self.next.y == y:
                return True
            else:
                return self.next.checkcollision(x,y)
        else:
            return False


#___________________________________________________________
#main functions
#___________________________________________________________
import time
import random
import socket
import json
import netifaces as ni

from math import ceil, sqrt
def updateinput():
    if mode == "c":
        global client_socket
        client_socket.recv(1024) #sync
    
    c = keyPoller.poll()
    list = []
    while not c is None:
        list.append(c)
        c = keyPoller.poll()

    if mode == "c":
        client_socket.send(json.dumps(list).encode())
    else:
        inputlist = []
        inputlist.append(list)
        if mode == "s":
            for client_socket in client_sockets:
                client_socket.send(("sync").encode())
                list = json.loads(client_socket.recv(1024).decode())
                inputlist.append(list)
        snakesdone = 0
        for list in inputlist:
            controller = inputlist.index(list)
            for c in list:
                if c == "27":
                    print("Game exited")
                    exit()
                elif c == "82":
                    initgame()
                num = -1
                for i in range(snakesdone, snakesdone+playernumlist[controller]):
                    snake = snakelist[i]
                    num += 1
                    if snake.isdisabled(): continue
                    if c == controls[num][0] and snake.head.direction != 1:#left
                        snake.setdirection(3)
                    elif c == controls[num][1] and snake.head.direction != 0:#up
                        snake.setdirection(2)
                    elif c == controls[num][2] and snake.head.direction != 3:#right
                        snake.setdirection(1)
                    elif c == controls[num][3] and snake.head.direction != 2:#down
                        snake.setdirection(0)     
            snakesdone += playernumlist[controller]
        
        
            
def updatesnake(): #updates the snake, returns true if the snake ate food
    returnvalue = False
    for snake in snakelist:
        if snake.isdisabled(): continue
        if snake.move(mapx,mapy,mapcollisions):
            snake.disable()
        collision = snake.checkcollision(snakelist)
        if collision != -1:
            snakelist[collision].disable()
        for food in foodlist:
            if snake.getheadxy() == food:
                foodlist.remove(food)
                snake.increaselength()
                returnvalue = True
    return returnvalue

def updatescreen():
    map = ""
    if mode == "c":
        global client_socket
        packet = client_socket.recv(1024).decode()
        client_socket.send("sync".encode())
        while packet != "end":
            map += packet
            packet = client_socket.recv(1024).decode()
            client_socket.send("sync".encode())
        map = map.replace("*","\n")
            
    else:
        #save map (map will not be printed but saved in a var until it is finished to avoid flickering)
        for snake in snakelist:
            map += "Points " + abc[snakelist.index(snake)] + ": " + str(snake.getlength()-2) + "   "
            if map.rfind("\n") < len(map)-mapx:
                map += "\n"
        if map.rfind("\n") < len(map)-1: map += "\n"
        for y in range(mapy):
            for x in range(mapx):
                found = False
                for snake in snakelist:
                    if snake.isdisabled(): continue
                    bodypositions = snake.getpositions()
                    num = snakelist.index(snake)
                    if (x,y) == snake.getheadxy():
                        map += abc[num]
                        found = True
                    elif (x,y) == snake.gettailxy():
                        map += "T"
                        found = True
                    elif (x,y) in bodypositions:
                        map += "X"
                        found = True
                if not found:
                    if (x,y) in foodlist:
                        map += "O"
                    else:
                        map += "."
            map += "\n"
        if mode == "s":
            copy = map.replace("\n","*")
            for client_socket in client_sockets:
                while len(copy) > 1024:
                    client_socket.send(copy[:1024].encode())
                    copy = copy[1024:]
                    client_socket.recv(1024)
                client_socket.send(copy.encode())
                client_socket.recv(1024)
                client_socket.send(("end").encode())
                client_socket.recv(1024)
    if not(mode == "s" and playernum == 0):
        #clear screen
        print("\033c")
        #print map
        print(map)
    
def get_local_ip():
    try:
        # Create a UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to an arbitrary external server
        local_ip = s.getsockname()[0]  # Get the IP address of the socket
        s.close()
        return local_ip
    except Exception as e:
        print("Error getting local IP:", e)
        return None

def get_available_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def initgame():
    global speed, foodlist, snakelist, controls
    speed = 1
    foodlist = []
    snakelist = []
    controls = [["37", "38", "39", "40"],["65", "87", "68", "83"],["75", "79", "192", "76"],["86", "71", "78", "66"]]
    subdivisions = ceil(sqrt(totalplayernum))+1
    poslist = []
    for y in range(1, subdivisions):
        for x in range(1, subdivisions):
            poslist.append((mapx//subdivisions*x,mapy//subdivisions*y))
    for i in range(totalplayernum):
        snakelist.append(Snake(poslist[i][0],poslist[i][1]))

#___________________________________________________________
#main program (what is run when the program is started)
#___________________________________________________________
print("Welcome to Snako!")

playernum = int(input("How many local players are playing? (1,4) or 0 to spectate / server only: "))
while playernum < 0 or playernum > 4:
    playernum = int(input("Invalid input. Write a number between 0 and 4: "))
firstplayer = 0
totalplayernum = playernum
playernumlist = [playernum]

if playernum == 0:
    online = "y"
    print("Online mode enabled for 0 local players.")
else:
    online = input("Do you want to play online? (y/n) ")
    while online != "y" and online != "n":
        online = input("Invalid input. Write y or n: ")

if online == "y":
    mode = input("Do you want to set up a server or connect to one? (s/c) ")
    while mode != "s" and mode != "c":
        mode = input("Invalid input. Write s or c: ")
    if mode == "s":
        if playernum == 0: print("You are on server only mode. You will not see the game screen.")
        connections = int(input("How many different computers will connect to the server? "))
        while connections < 1:
            connections = int(input("Invalid input. Write a number greater than 0: "))
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        manual = input("Do you want to set the ip and port manually? (y/n) ")
        while manual != "y" and manual != "n":
            manual = input("Invalid input. Write y or n: ")
        if manual == "y":
            ip = input("Write the IP of the server: ")
            port = int(input("Write the port of the server: "))
        else:
            ip = get_local_ip()
            port = get_available_port()
        server_address = (ip, port)
        server_socket.bind(server_address)
        print("IP: " + ip + " Port: " + str(port))
        print("Server set up. Waiting for connections...")
        server_socket.listen(connections)
        client_sockets = []
        for i in range(connections):
            client_socket, client_address = server_socket.accept()
            client_sockets.append(client_socket)
            print("Connection from " + str(client_address))
            client_socket.send(str(totalplayernum).encode())
            clientplayernum = int(client_socket.recv(1024).decode())
            playernumlist.append(clientplayernum)
            totalplayernum += clientplayernum
        print("All connections established.")
    else:
        if playernum == 0: print("You are on spectator mode. You will not move any snake.")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = input("Write the IP of the server: ")
        server_port = int(input("Write the port of the server: "))
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_address, server_port))
        firstplayer = int(client_socket.recv(1024).decode())
        client_socket.send(str(playernum).encode())
        print("Connection established.")
else: mode = ""
if online == "n" or mode == "s":  
    mapx = int(input("How wide do you want the map to be? "))
    mapy = int(input("How high do you want the map to be? "))
    foodnum = int(input("How many food do you want in the map? "))
    while mapx < 10 and mapy < 10 and foodnum <= 0:
        print("The map has to be at least 10x10. Food number has to be more than 0.")
        mapx = int(input("How wide do you want the map to be? "))
        mapy = int(input("How high do you want the map to be? "))
        foodnum = int(input("How many food do you want in the map? "))
    mapcollisions = input("Do you want to enable collisions with the edges of the map? (y/n) ")
    while mapcollisions != "y" and mapcollisions != "n":
        mapcollisions = input("Invalid input. Write y or n.")
    if mapcollisions == "y": mapcollisions = True
    else: mapcollisions = False

print("Controls:")
abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
controlstext = ["arrows","WASD","OKLÑ","GVBN"]
for i in range(playernum):
    print("Player " + abc[i+firstplayer] + ": " + controlstext[i])
print("ESC to exit the game")
print("R to restart the game")
print("Press enter to start the game:")
input()
if mode == "c":
    print("Waiting for server to start the game...")
    client_socket.send("start".encode())
    client_socket.recv(1024)
elif mode == "s":
    print("Waiting for all clients to start the game...")
    for client_socket in client_sockets:
        client_socket.recv(1024)
    for client_socket in client_sockets:
        client_socket.send("start".encode())

with KeyPoller() as keyPoller:
    if mode != "c":
        global speed, foodlist, snakelist, controls
        initgame()
    while True:
        updateinput()
        if mode != "c":
            if updatesnake(): speed *= 1.1
            if len(foodlist) < foodnum:
                newfood = (random.randint(0,mapx-1),random.randint(0,mapy-1))
                foodlist.append(newfood)
        updatescreen()
        if mode != "c": time.sleep(0.5/speed)