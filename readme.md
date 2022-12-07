## Implementing 3NIM game using peer to peer networking

This project is part of a Distributed System(CSM13001) course of University of Helsinki.

Peer-to-peer is a network structure most used in sharing networks. This structure has made games more socially interactive. So we implemented a multiplayer game of three players and a queue of items. The queue has two types of items: 0:s and 1:s. The players take turns removing either one or two items from the queue. If a player removes a 0 from the queue, the player drops out of the game. The last player left in the game wins.

The structure of the queue is as follows: There are always two 0:s in the queue, one of which is the last item of the queue. The other items are 1:s. We implement a static version of the game. The length of the queue is the same in every game and the first 0 is always placed at the halfway point of the queue. It is also possible to vary the length of the queue and the placement of the first 0. Also, the items are referred to as 0:s and 1:s here.

## Technological choices 

There is one server and three clients(players). So there are 4 nodes in total.Each node is working on sepearte virtual machines. And each one of the nodes has their own IP-address. We will be using VirtualBox as our virtual machine platform. The machines all run Linux Ubuntu operating system. We chose python as our programming language. And have created a text-based command line user interface. 
Messages will be structured as name-value pairs in a dictionary-like manner and have used a JSON-RPC library for message delivery.
All the requirements for the project can be found in [Github](https://github.com/distributed-group/nim-game/blob/main/requirements.txt)

## Design

All the players send an initial message to the server about their intention to play. Once the server receives all 3 requests from the players, it sends all the 3 IP-addresses of the nodes to the last node that requested it along with a message “ready to start”. Once the node receives this message, it starts establishing a connection with its two other peer nodes. The last node connects with nodes 1 and 2. Then nodes 1 and 2 share the IP addresses to establish a connection between themselves. Finally, all the nodes(players) connect to and rely upon each other to keep the network going. It is shown in [github repository](https://github.com/distributed-group/nim-game/blob/main/client.py).

We implement our p2p application by extending Node and NodeConnection classes. We have tried to do in a similar way as shown in [Python implementation of a peer-to-peer decentralized network](https://github.com/macsnoeren/python-p2p-network).
Each node provides a TCP/IP server on a specific port to provide inbound nodes to connect. The same node is able to connect to other nodes, called outbound nodes. And we are able to send a message over the TCP/IP channel to the connected (inbound and outbound) nodes as shown in this [repository](https://github.com/distributed-group/nim-game/blob/main/NimPeerNode.py).

[NimPeerNode](https://github.com/distributed-group/nim-game/blob/main/NimPeerNode.py) class initializes the game and handles all the changes of states of each node.All the state of nodes are handled by this class. The game starts when[NimGame](https://github.com/distributed-group/nim-game/blob/main/NimGame.py) class is called.





 