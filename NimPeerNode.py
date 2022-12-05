from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
from NimGame import NimGame
import time
import socket

p2p_port = 10001

class NimPeerNode (Node):

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        self.nimgame = None
        self.myip = host
        super(NimPeerNode, self).__init__(host, port, id, callback, max_connections)

    """
    This function is invoked when another node sends this node a message.
    """
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

    """ 
    The message is an initial connecting message.
    Before statring the game, we try to connect to the two peers.
    """
    def status_connecting(self, data):
        first_peer_ip = data['player1']
        second_peer_ip = data['player2']
        # Collect IP addresses of nodes connected to this node
        connected_nodes = super(NimPeerNode, self).all_nodes
        conn_hosts = []
        for node in connected_nodes:
            conn_hosts.append(node.host)
        # Don't connect if connection exists or is node itself
        if self.my_ip != first_peer_ip and first_peer_ip not in conn_hosts:
            super(NimPeerNode, self).connect_with_node(first_peer_ip, p2p_port)
        if self.my_ip != second_peer_ip and second_peer_ip not in conn_hosts:
            super(NimPeerNode, self).connect_with_node(second_peer_ip, p2p_port)
        data['status'] = 'start game'
        super(NimPeerNode, self).send_to_nodes(data)
    
    """ 
    Let's start the game.
    """
    def status_start_game(self, data):
        self.nimgame = NimGame(self.my_ip, data['player1'], data['player2'], data['player3'])
        self.handle_turn(data)

    """ 
    Someone has made a move, update the game state.
    """
    def status_move(self, data):
        self.nimgame.update_state(data['state'])
        # Give some time for the game to update the state
        time.sleep(2)
        self.handle_turn(data)

    """
    Handles one turn...?
    """
    def handle_turn(self, data):
        new_state = self.nimgame.turn_manager()
        if new_state:
            data['status'] = 'move'
            data['state'] = new_state
            super(NimPeerNode, self).send_to_nodes(data)

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

    def create_new_connection(self, connection, id, host, port):
        return NodeConnection(self, connection, id, host, port)