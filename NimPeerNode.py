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
import printer #Refactor this dependency away later

load_dotenv()
p2p_port = 10001
server_port = 5001
TURN_TIMEOUT = 20.0

class NimPeerNode (Node):

    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        self.game = None
        self.myip = host
        self.timer = threading.Timer(TURN_TIMEOUT, self.alarm)
        super(NimPeerNode, self).__init__(host, port, id, callback, max_connections)

    """
    This function is invoked when another node sends this node a message.
    Based on the message's status code, this function decides what to do next.
    Since all information is communicated through messages, this is the starting point for all actions this node takes.
    """
    def node_message(self, connected_node, data):

        self.my_ip = socket.gethostbyname(socket.gethostname())
        print("Message from " + connected_node.host + ": " + str(data))

        if 'status' in data.keys():

            self.stop_old_timer()

            if data['status'] == 'connecting':

                self.status_connecting(data)

            elif data['status'] == 'start game' and not self.game:

                self.status_start_game(data)
                self.set_timer()

            elif data['status'] == 'move':
                # Update local game state based on the received messagef
                self.game.update_state(data['state'])
                # Give some time for the game to update the state
                time.sleep(1)
                # Decide what to do (display game state and if our turn, make a move)
                self.action(data)
                self.set_timer()

            elif data['status'] == 'peer_disconnect':
                self.game.update_state(data['state'])
                self.action(data)

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
        if not self.game:
            my_number = self.get_player_number(data)
            self.game = NimGame(self.my_ip, my_number, data['1'], data['2'], data['3'])
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
    Decides what to do after a message has been received.
    If it is our turn: 
        1. We show the current state
        2. Make a move (updating our local state again)
        3. Broadcast the new state to others
    If it is not our turn, we only show the current state.
    TODO: The user has x seconds to make a move. Countdown is displayed to the user.
    """
    def action(self, data):
        self.game.display_game_state()
        if self.game.our_turn():
            updated_state = self.game.make_move()
            data['status'] = 'move'
            data['state'] = updated_state
            super(NimPeerNode, self).send_to_nodes(data)
        
    """
    """
    def create_message(self, status, state):
        data = {}
        data['1'] = self.game.state['players'][0]
        data['2'] = self.game.state['players'][1]
        data['3'] = self.game.state['players'][2]
        data['status'] = status
        data['state'] = state
        return data


    # MANAGE CONNECTIONS

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
        

    # TIMER RELATED FUNCTIONS

    """
    Deletes the previous timer. Creates a new timer.
    """
    def stop_old_timer(self):
        if self.timer.is_alive():
            self.timer.cancel()
            self.timer = threading.Timer(TURN_TIMEOUT, self.alarm)

    """
    Sets the timer.
    """
    def set_timer(self):
        if not self.timer.is_alive():
            self.timer.start()

    """
    This function is executed when the alarm goes off.
    """
    def alarm(self):
        # First we add the current player to lost players
        disconnected_player = self.game.get_current_player()
        self.game.add_player_to_lost(disconnected_player)
        # Disconnect from the disconnected node
        #self.disconnect_from_dead_node(disconnected_player)
        if self.game.is_end(): # Only one player left, so we announce the winner
            # We update our own state
            winner = self.game.update_winner()
            self.game.set_announcement(printer.disconnect_and_winner(disconnected_player, winner))
        else: # The game ends with no winner
            # We update our own state
            self.game.set_phase('ended_no_winner')
            self.game.set_announcement(printer.disconnect(disconnected_player))
        # Let the other node know as well
        super(NimPeerNode, self).send_to_nodes(self.create_message('peer_disconnect', self.game.state))
        #Show the end screen to player
        self.game.display_game_state()

    """
    When node want's to disconnect with not responding node
    """
    def disconnect_from_dead_node(self, disconnected_player):
        disconnected_ip = self.game.state['players'][disconnected_player-1]
        print('disconnected ip is', disconnected_ip)
        print('disconnected player is ', disconnected_player)
        conn_hosts = []
        for conn in super(NimPeerNode, self).all_nodes:
            conn_hosts.append(conn.host)
            if conn.host == disconnected_ip:
                while len(super(NimPeerNode, self).all_nodes) > 1:
                    super(NimPeerNode, self).disconnect_with_node(conn.stop())
                    time.sleep(5)

