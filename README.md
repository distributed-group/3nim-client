## 3NIM

This project was done as group work for course "Distributed Systems" in University of Helsinki.

[Nim game](https://en.wikipedia.org/wiki/Nim) is a famous mathematical strategy game. This project implements a three-player version of the game with one queue titled "3NIM". The basic idea of the game is as follows: The queue has two types of items, 0s and 1s. The players take turns removing either one or two items from the queue. If a player removes a 0 from the queue, that player drops out of the game. The last player left in the game wins.

The main objective of this project was to learn how to design and program a simple distributed system. Our application has a game server that clients can contact to start a game and all communication during the game happens peer-to-peer (P2P) between the clients. This repository has the client side code in it. The server side code can be found [here](https://github.com/distributed-group/3nim-server). For a more detailed description of system architecture and communication, please look at "Documentation" -section below.

The peer-to-peer communication is implemented using library [p2pnetwork](https://github.com/macsnoeren/python-p2p-network). The client-server communication happens through remote procedure calls. For this we used [jsonrpclib](https://pypi.org/project/jsonrpclib/) on the client side and [jsonrpcserver](https://pypi.org/project/jsonrpcserver/) on the server side.

## Requirements

This game is planned to run in Ubuntu operating system. You need also Python and pip installed. 

Server and every game client must run on different machines so that everyone has their unique ip-address. To test the game, you will need 4 different machines connected to the same network.

## Download and start the game server

Download the [game server](https://github.com/distributed-group/3nim-server).

Navigate to the folder where server.py is located, and install the dependencies by ```pip install -r requirements.txt```.

Start the game server by typing ```python3 server.py```

## Download and start the game

Download the game client from this repository.

Navigate to the folder where client.py is located. You need to create a file called ```.env```. File content should be:
```SERVER_IP="00.00.00.00"```, where the the ip-address is replacing the zero-string.

Install client dependencies by ```pip install -r requirements.txt```

Make sure your game server is running first.

Start the game by typing ```python3 client.py``` in the terminal

You are first placed to the player queue in the server side. When there are three players in the queue, the game starts.

## How to play

You will see the fresh game state always in the bottom of the screen. There are blue sticks and red rotten apples.
When it is your turn, you need to decide if you want to pick 1 or 2 items. If you pick a rotten apple, you lose. The last player in the game, who has not picked the rotten apple, is the winner.

## Program construction

```client.py``` is handling the initial contact to the game server and starting the actual client node.

```NimPeerNode``` has functionalities to react to the messages which the client node receives.

```NimGame``` contains the game logic.

```printer.py``` does printings to the terminal and has some helper functions

```Logger``` writes to the log file.
