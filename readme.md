## Implementing 3NIM game using peer to peer networking

The game consists of three players and a queue of items. The queue has two types of items: X:s and O:s. The players take turns removing either one or two items from the queue. If a player removes an X from the queue, the player drops out of the game. The last player left in the game wins.

We implement our p2p application by extending Node and NodeConnection classes. And extended the class Node and NodeConnection. 

## Extend class Node

'class NimPeerNode (Node):

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
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
        print("node is requested to stop!")'
    
## NodeConnection class

' def create_new_connection(self, connection, id, host, port):
        return NodeConnection(self, connection, id, host, port)'
