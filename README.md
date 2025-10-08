# Snako Online

This project is a Python console-based implementation of the popular Snake game, but with multiplayer functionalities.

The multiplayer mode is highly customizable and scalable, with several options available:

 - Local single-player
 - Local multiplayer (up to 4 players on the same keyboard)
 - Online multiplayer (one server and infinite clients). The server itself is also a player.
 - Combination of local and online: Each connected machine on online mode can run 4 different players, so with 2 machines (one server and one client) you can have up to 8 players.
 - Server-only mode: Server can decide to not be a player and just host the game.
 - Online spectator: Online clients can decide to just spectate the game and not control any player.

## Usage

The input system currently works only on Windows. However, a Linux machine can be used as a server with no players.

To use the project, simply install python3 and the dependencies
```
pip install requirements.txt
```
And then run the game
```
python3 snako_online.py
```
The game is played entirely on the console, so it is recommended to keep it full screen so the map can be bigger without flickering.

When the program starts, you will be asked to set up the game parameters:

- Local players: The number of players on your machine (up to 4 players on the same keyboard). If your machine will be just a server or a spectator client, input 0.
- Online mode: You need to input "y" either if you are connecting to a server or you are the server itself. If the local players number is 0, it will be set to yes as you cannot play a local game with 0 players.
- Server/connect: On online mode, one machine will be the server and the rest will be clients. If you want to play outside a local network, your server should be accessible through the internet.
- If you selected server, you will be asked to the number of clients that will connect. After that, you can write the ip/port manually (useful when playing through the internet and you need to use a specific port for firewall purposes), or let the program assign it for you. Then the server will wait for all connections.
- If you selected client, write the ip and port of the server (type the public ip if you are playing through the internet).
- Finally, if you are the online server or you are just playing locally, you will need to set up the map parameters (width/heigh/collisions/food).
- Before starting the game, each machine will display the controls for each of their local players. When you are ready, press enter, and when all machines are ready, the game will start.

## Gameplay

The snakes will start with lengh 2. The head of the snake is the letter of the player (A, B, C...), and the tail will be a T.

When a snake eats a piece of food (O), it will grow on size and the game will get faster.

Snakes can collide with themselves and with other snakes. They can also collide with the edge of the map if edge collisions are turned on. Otherwise, they will appear on the opposite side.

The game will display the points of each Snake. Once all snakes are deleted, you will not see a "game over" screen, but you can compare the points to determine the winner.

Any machine can restart the game at any time pressing R, or exit the program entirely pressing "esc". If any player presses "esc", the game will terminate for all players.

## Project future

This was a "for fun" project, and it is far from being perfect. Here are some things I will (or not) be working in to improve the game:

- Make the input work on Linux machines
- Improve network load by sending just the game data and letting the clients render the map themselves. Right now the server sends the whole text that forms the map.
- Making the speed scaling actually infinite. Now, the real speed is limited by how fast the computer can print on the console. This can cause issues when a high performant server is connected to a low performant client. The solution would be to start skipping frames when the speed is too high.
- Eliminate flickering. This would be a consequence of the frame skip system, as once frames can be skipped, the framerate can be limited to avoid flickering.

## Contact

If you want to contact me you can write an issue on the repo or send me an email to ruben.lr3@gmail.com