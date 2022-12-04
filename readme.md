## Implementing 3NIM game using peer to peer networking

The game consists of three players and a queue of items. The queue has two types of items: X:s and O:s. The players take turns removing either one or two items from the queue. If a player removes an X from the queue, the player drops out of the game. The last player left in the game wins.

We implement our p2p application by extending Node and NodeConnection classes. And extended the class Node and NodeConnection. 

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

Messages will be structured as name-value pairs in a dictionary-like manner. We have used a JSON-RPC library for message delivery. The system has two types of nodes: servers and clients. Initially there will be one server and three clients, making four nodes in total. 

The server is the initial point of contact for the clients. The clients know the server’s IP address and contact it by sending an initial message informing the server of their will to participate in a game. In this same message the clients tell the server their IP address.
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


### When the client receives 'ready to start' -message, it connects with two peers. 
```python
def start_game(peer_ips):
    first_peer_ip = peer_ips['player1']
    second_peer_ip = peer_ips['player2']

    #Connect with the other two nodes, 1 and 2
    node.connect_with_node(first_peer_ip, p2p_port)
    node.connect_with_node(second_peer_ip, p2p_port)
    time.sleep(2)

    #Shares the IP addresses to nodes 1 and 2 so they can reach each other
    peer_ips['status'] = 'connecting'
    node.send_to_nodes(peer_ips)
```

### The node that is connected to the server will check whether all nodes are connected with each other before starting the game.
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
### Before starting the game, we try to connect if the connection is not established yet.

```python

``` 


### If all client nodes are connected with each other, then the game starts.

```python
def status_start_game(self, data):
        self.nimgame = NimGame(self.my_ip, data['player1'], data['player2'], data['player3'])
        self.handle_turn(data)

```
### If the game has already started and a player makes a move

```python
def status_move(self, data):
        self.nimgame.update_state(data['state'])
        # Give some time for the game to update the state
        time.sleep(2)
        self.handle_turn(data)
```

#### To handle turn of each player

```python
def handle_turn(self, data):
        new_state = self.nimgame.turn_manager()
        if new_state:
            data['status'] = 'move'
            data['state'] = new_state
            super(NimPeerNode, self).send_to_nodes(data)
```
