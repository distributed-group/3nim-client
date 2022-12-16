## 3NIM

This project was done as group work for course "Distributed Systems" in University of Helsinki.

[Nim game](https://en.wikipedia.org/wiki/Nim) is a famous mathematical strategy game. This project implements a three-player version of the game with one queue titled "3NIM". The basic idea of the game is as follows: The queue has two types of items, 0s and 1s. The players take turns removing either one or two items from the queue. If a player removes a 0 from the queue, that player drops out of the game. The last player left in the game wins.

The main objective of this project was to learn how to design and program a simple distributed system. Our application has a game server that clients can contact to start a game and all communication during the game happens peer-to-peer (P2P) between the clients. This repository has the client side code in it. The server side code can be found [here](https://github.com/distributed-group/3nim-server). For a more detailed description of system architecture and communication, please look at "Documentation" -section below.

The peer-to-peer communication is implemented using library [p2pnetwork](https://github.com/macsnoeren/python-p2p-network). The client-server communication happens through remote procedure calls. For this we used [jsonrpclib](https://pypi.org/project/jsonrpclib/) on the client side and [jsonrpcserver](https://pypi.org/project/jsonrpcserver/) on the server side.


## Download and start the game

Download the game client. Note that this is only the client side of the game, you need also the game [server](https://github.com/distributed-group/3nim-server).
Navigate to the folder where client.py is located. You need to create a file called ```.env```. File content should be:
```SERVER_IP="00.00.00.00"```, where the the ip-address is replacing the zero-string.

Install client dependencies by pip freeze < requirements.txt

Make sure your game server is running first.

Start the game by typing ```python3 client.py``` in the terminal

You are first placed to the player queue in the server side. When there are three players in the queue, the game starts.

## How to play

You will see the fresh game state always in the bottom of the screen. There are blue sticks and red rotten apples.
When it is your turn, you need to decide if you want to pick 1 or 2 items. If you pick a rotten apple, you lose. The last player in the game, who has not picked the rotten apple, is the winner.

## Documentation

Detailed description of the system can be found here.
- Link to the final report?
- ...Something else?
