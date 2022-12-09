## 3NIM

This project was done as group work for course "Distributed Systems" in University of Helsinki.

[Nim game](https://en.wikipedia.org/wiki/Nim) is a famous mathematical strategy game. This project implements a three-player version of the game with one queue titled "3NIM". The basic idea of the game is as follows: The queue has two types of items, 0s and 1s. The players take turns removing either one or two items from the queue. If a player removes a 0 from the queue, that player drops out of the game. The last player left in the game wins.

The main objective of this project was to learn how to design and program a simple distributed system. Our application has a game server that clients can contact to start a game and all communication during the game happens peer-to-peer (P2P) between the clients. This repository has the client side code in it. The server side code can be found [here](https://github.com/distributed-group/3nim-server). For a more detailed description of system architecture and communication, please look at "Documentation" -section below.

The peer-to-peer communication is implemented using library [p2pnetwork](https://github.com/macsnoeren/python-p2p-network). The client-server communication happens through remote procedure calls. For this we used [jsonrpclib]() (still missing link) on the client side and [jsonrpcserver](https://www.jsonrpcserver.com/en/stable/index.html) (is this link correct?) on the server side.


## Download the game

- How to download the program
- How to run the program ... starting point is client.py.

## How to play

- Instructions on how to play the game (screenshots?)

## Documentation

Detailed description of the system can be found here.
- Link to the final report?
- ...Something else?
