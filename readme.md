## Implementing 3NIM game using peer to peer networking

The game consists of three players and a queue of items. The queue has two types of items: X:s and O:s. The players take turns removing either one or two items from the queue. If a player removes an X from the queue, the player drops out of the game. The last player left in the game wins.
The structure of the queue is as follows: There are always two X:s in the queue, one of which is the last item of the queue. The other items are O:s. We will first implement a static version of the game. This means that the length of the queue is the same in every game and the first X is always placed at the half point of the queue. It is also possible to vary the length of the queue and the placement of the first X. Also, the items are referred to as X:s and O:s here, but they could be anything from fruits to numbers, as long as it is clear which items cause a player to lose.

We implement our p2p application by extending Node and NodeConnection classes. 
 Messages will be structured as name-value pairs in a dictionary-like manner. We have used a JSON-RPC library for message delivery. The system has two types of nodes: servers and clients. Initially there will be one server and three clients, making four nodes in total.

 NimPeerNode is the class which forms all the client node.

## Extend class Node
``` python
class NimPeerNode (Node):

    def __init__(self, host, port, id=None, callback=None, max_connections=0)`:
        self.nimgame = None
        self.myip = host
        super(NimPeerNode, self).__init__(host, port, id, callback, max_connections)

    def outbound_node_connected(self, connected_node):
        print("outbound_node_connected: " + connected_node.id)
        
    def inbound_node_connected(self, connected_node):
        print("inbound_node_connected: " + connected_node.id)

    def inbound_node_disconnected(self, connected_node):
        print("inbound_node_disconnected: " + connected_node.id)
        print('trying get connection back')
        super(NimPeerNode, self).connect_with_node(connected_node.host, p2p_port)

    def outbound_node_disconnected(self, connected_node):
        print("outbound_node_disconnected: " + connected_node.id)
        
    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)
        
    def node_request_to_stop(self):
        print("node is requested to stop!")
```
    
## NodeConnection class

```python
    def create_new_connection(self, connection, id, host, port):
        return NodeConnection(self, connection, id, host, port)
```

 

The server is the initial point of contact for the clients. The clients know the server’s IP address and contact it by sending an initial message informing the server of their will to participate in a game. In this same message the clients tell the server their IP address.

```python
    def node_message(self, connected_node, data):

        self.my_ip = socket.gethostbyname(socket.gethostname())
        print("Message from " + connected_node.host + ": " + str(data))

        if 'status' in data.keys():
            if data['status'] == 'connecting':

                self.status_connecting(data)
        

        elif data['status'] == 'start game' and not self.nimgame:

            self.status_start_game(data)

        elif data['status'] == 'move':

            self.status_move(data)
```

***Initial connecting message***
```python
    def status_connecting(self, data):
        second_peer_ip = data['player2']
        first_peer_ip = data['player1']
        self.connect_with_peers(first_peer_ip, second_peer_ip)
        data['status'] = 'start game'
        super(NimPeerNode, self).send_to_nodes(data)
```

***Function to connect with peers***
```python
    def connect_with_peers(self, first_peer_ip, second_peer_ip):
        # Collect connected nodes IP addresses
        connected_nodes = super(NimPeerNode, self).all_nodes
        conn_hosts = []
        for node in connected_nodes:
            conn_hosts.append(node.host)
        # Don't connect if connection exists or is node itself
        if self.my_ip != first_peer_ip and first_peer_ip not in conn_hosts:
            super(NimPeerNode, self).connect_with_node(first_peer_ip, p2p_port)
        if self.my_ip != second_peer_ip and second_peer_ip not in conn_hosts:
            super(NimPeerNode, self).connect_with_node(second_peer_ip, p2p_port)
```

When the the server collects all three IP addresses, it then sends it to the last node that requested to the server.Then the last node connects with node 1 and 2. Then nodes 1 and 2 establishes connection between them. Finally, when all nodes are connected to each other, they receive the status ```python data['status'] = 'start game'``` .Then they start the game.

### If all client nodes are connected with each other, then the game starts.

```python
    def status_start_game(self, data):
        self.nimgame = NimGame(self.my_ip, data['player1'], data['player2'], data['player3'])
        self.handle_turn(data)

```

## NimGame is the class which has all the conditions for the game.

The class is initialized with the __init__() function.

```python

    def __init__(self, my_ip, player1, player2, player3):
        self.my_ip = my_ip
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.state = {'sticks': [1,1,1,1,1,0,1,1,1,1,0],
                        'last': None,
                        'last_move': None,
                        'last_note': 'Waiting first player to start',
                        'next': player1,
                        'phase': 'starting',
                        'lost': [],
                        'players': [player1, player2, player3],
                        'winner': None,
                        'moves_count': 0}

```
## Change state of player
When its time to change state of player ``` handle_turn(data)``` function is called.
```python
    def handle_turn(self, data):
        new_state = self.nimgame.turn_manager()
        if new_state:
            data['status'] = 'move'
            data['state'] = new_state
            super(NimPeerNode, self).send_to_nodes(data)
```
It then calls the function ```turn_manager()``` from the NimGame class to count the moves of each player and update the state accordingly.
```python
    def turn_manager(self):
        if self.state['phase'] == 'ended':
            self.show_end_game()
        elif self.state['next'] == self.my_ip and self.my_ip not in self.state['lost']:
            self.show_game()
            self.state['phase'] = 'playing'
            pr.print('', color='yellow')
            print('_______It is your turn_______')
            print('Do you want to pick one or two sticks?')
            answer = int(input())
            self.pick_sticks(answer, self.my_ip)
            self.state['last'] = self.my_ip
            self.state['last_move'] = answer
            self.state['moves_count'] = self.state['moves_count'] + 1
            self.state['next'] = self.state['players'][(self.state['moves_count']) % 3]
            if self.state['phase'] == 'ended':
                self.show_end_game()
                return self.state
            self.show_game()
            return self.state
        elif self.state['next'] == self.my_ip and self.my_ip in self.state['lost']:
            self.state['moves_count'] = self.state['moves_count'] + 1
            self.state['next'] = self.state['players'][(self.state['moves_count']) % 3]
            return self.state
        else:
            self.show_game()
```
## Move by a player

If one of the player has made a move, the state changes with the ```status_move()``` function.
```python
    def status_move(self, data):
        self.nimgame.update_state(data['state'])
        # Give some time for the game to update the state
        time.sleep(2)
        self.handle_turn(data)
```
This calls another function of ``` update_state()``` from NimGame class
```python 
    def update_state(self, new_state):
        if abs(new_state['moves_count'] < self.state['moves_count']):
                # Don't update from older state
                print('ERROR! Moves out of syncronization!')
            else:
                self.state = new_state
```


            