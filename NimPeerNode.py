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
    We try to connect to the peers.
    This code is executed by nodes 1 and 2. However, only node 1 acts.
    """
    def status_connecting(self, data):
        first_peer_ip = data['1']
        second_peer_ip = data['2']
        if self.my_ip == first_peer_ip:
            super(NimPeerNode, self).connect_with_node(second_peer_ip, p2p_port)
            data['status'] = 'start game'
            super(NimPeerNode, self).send_to_nodes(data)
    
    """ 
    Let's start the game.
    """
    def status_start_game(self, data):
        second_peer_ip = data['2']
        if self.my_ip == second_peer_ip:
            #inform node 1 that, 'start game' is received it can also start
            super(NimPeerNode, self).send_to_nodes(data)
        # Create the local game state
        my_number = self.get_player_number(data)
        self.nimgame = NimGame(self.my_ip, my_number, data['1'], data['2'], data['3'])
        # Decide on an action
        self.action(data)

    """
    Find own player number from the start game message.
    """
    def get_player_number(self, data):
        for number in data:
            if (data[number] == self.my_ip):
                return number
        return 0

    """ 
    Someone has made a move: Update the game state and decide on an action.
    """
    def status_move(self, data):
        # Update local state based on the received message
        self.nimgame.update_state(data['state'])
        # Give some time for the game to update the state
        time.sleep(2)
        # Decide on an action
        self.action(data)

    """
    Decides what to do after a message has been received.
    If it is our turn, we show the current state, make a move, update our local state, show it to the user and broadcast the new state to others.
    TODO: The user has x seconds to make a move. Countdown is displayed to the user.
    If it is not our turn, we only show the current state.
    TODO: Always after considering an action, whether we made a move or not, we need to set the timer.
    """
    def action(self, data):
        self.nimgame.display_game_state()
        if self.nimgame.our_turn():
            updated_state = self.nimgame.make_move()
            if updated_state:
                data['status'] = 'move'
                data['state'] = updated_state
                super(NimPeerNode, self).send_to_nodes(data)
        # Timer needs to be set here
        self.set_timer()
    
    """
    Sets an alarm that goes off in x seconds. Calling this function resets the alarm. Action is taken, if the alarm goes off.
    """
    def set_timer(self):
        kakka_ajastin = ""

    def outbound_node_connected(self, connected_node):
        super(NimPeerNode, self).print_connections()
        print("outbound_node_connected: " + connected_node.id)
        
    def inbound_node_connected(self, connected_node):
        super(NimPeerNode, self).print_connections()
        print("inbound_node_connected: " + connected_node.id)

    def inbound_node_disconnected(self, connected_node):
        super(NimPeerNode, self).print_connections()
        #print("inbound_node_disconnected: " + connected_node.id)
        connected_nodes = super(NimPeerNode, self).all_nodes
        #if connected_node not in connected_nodes:
            #print('trying get connection back')
            #super(NimPeerNode, self).connect_with_node(connected_node.host, p2p_port)

    def outbound_node_disconnected(self, connected_node):
        super(NimPeerNode, self).print_connections()
        #print("outbound_node_disconnected: " + connected_node.id)
        connected_nodes = super(NimPeerNode, self).all_nodes
        #if connected_node not in connected_nodes:
            #print('trying get connection back')
            #super(NimPeerNode, self).connect_with_node(connected_node.host, p2p_port)
        
    def node_disconnect_with_outbound_node(self, connected_node):
        super(NimPeerNode, self).print_connections()
        print("node wants to disconnect with oher outbound node: " + connected_node.id)
        
    def node_request_to_stop(self):
        print("node is requested to stop!")

    def create_new_connection(self, connection, id, host, port):
        return NodeConnection(self, connection, id, host, port)