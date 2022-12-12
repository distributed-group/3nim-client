from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
from dotenv import load_dotenv
from NimGame import NimGame
from jsonrpclib import Server
import time
import sys
import os
import threading
import socket

load_dotenv()
p2p_port = 10001
server_port = 5001
TURN_TIMEOUT = 20.0

class NimPeerNode (Node):

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        self.nimgame = None
        self.myip = host
        self.timer = threading.Timer(TURN_TIMEOUT, self.alarm)
        self.last_setup = 0
        super(NimPeerNode, self).__init__(host, port, id, callback, max_connections)

    """
    This function is invoked when another node sends this node a message.
    """
    def node_message(self, connected_node, data):

        self.my_ip = socket.gethostbyname(socket.gethostname())
        print("Message from " + connected_node.host + ": " + str(data))

        if 'status' in data.keys():
            # Delete the previous timer and turn it off. Create a new timer.
            if self.timer.is_alive:
                self.timer.cancel()
                self.timer = threading.Timer(TURN_TIMEOUT, self.alarm)
            if data['status'] == 'connecting':
                self.status_connecting(data)
            elif data['status'] == 'start game' and not self.nimgame:
                self.status_start_game(data)
                if not self.timer.is_alive():
                    # Set the timer
                    self.last_setup = time.time()
                    self.timer.start()
            elif data['status'] == 'move':
                self.status_move(data)
                # Reset timer
                self.last_setup = time.time()
                self.timer.start()
            elif data['status'] == 'peer_disconnect':
                self.nimgame.update_state(data['state'])
                self.nimgame.display_game_state()

    """
    This function is executed when the alarm goes off.
    """
    def alarm(self):
        # For now this is the only thing we do:
        # Add the current player to lost
        disconnected_player = self.nimgame.state['player_in_turn']
        if disconnected_player not in self.nimgame.state['lost']:
            self.nimgame.state['lost'].append(disconnected_player)
        # Print announcement about this to the player
        print("Player " + str(disconnected_player) + " has disconnected.")
        print("The alarm went off in " + str(time.time() - self.last_setup) + " seconds.")

        if len(self.nimgame.state['lost']) >= 2: #Peer disconnecting has ended the game, since one player had already lost before that
            # We update our own state
            self.nimgame.update_winner()
            self.nimgame.state['announcement'] = "Player " + str(disconnected_player) + " has disconnected and player " + str(self.nimgame.state['winner']) + " has won!"
        else:
            # We update our own state
            self.nimgame.state['announcement'] = "Player " + str(disconnected_player) + " has left the game.\nThe game has ended."
            self.nimgame.state['phase'] = 'ended_no_winner'
        # Let the other node know as well
        super(NimPeerNode, self).send_to_nodes(self.create_message('peer_disconnect'))
        #Show the end screen to player
        self.nimgame.display_game_state()
    
    def create_message(self, status):
        game = self.nimgame
        data = {}
        data['1'] = game.state['players'][0]
        data['2'] = game.state['players'][1]
        data['3'] = game.state['players'][2]
        data['status'] = status
        data['state'] = self.nimgame.state
        return data

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
        # Let's inform the server we are connected to two if so
        if len(super(NimPeerNode, self).all_nodes) >= 2:
            print('informing server about two peers')
            self.we_are_connected(data)
        second_peer_ip = data['2']
        if self.my_ip == second_peer_ip:
            #inform node 1 that, 'start game' is received it can also start
            super(NimPeerNode, self).send_to_nodes(data)
        # Create the local game state
        if not self.nimgame:
            my_number = self.get_player_number(data)
            self.nimgame = NimGame(self.my_ip, my_number, data['1'], data['2'], data['3'])
            # Decide on an action
            self.action(data)

    def we_are_connected(self, data):
        #Connect to json-rpc server
        server_ip = os.getenv("SERVER_IP")
        server = Server('http://' + server_ip + ':' + str(server_port))
        
        # Lets send this message so long that server answers to it
        while True:
            print('Informing server about the succesful connection with 2 peers')
            try:
                res = server.connected_to_two(data['game_id'], self.my_ip)
                if res['received']:
                    break
            except:
                print('Error: ', sys.exc_info())
            time.sleep(2)

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
    """
    def action(self, data):
        self.nimgame.display_game_state()
        if self.nimgame.our_turn():
            updated_state = self.nimgame.make_move()
            data['status'] = 'move'
            data['state'] = updated_state
            super(NimPeerNode, self).send_to_nodes(data)

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