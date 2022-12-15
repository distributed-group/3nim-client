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
import printer


load_dotenv()


p2p_port = 10001
server_port = 5001
TURN_TIMEOUT = 20.0


# Different statuses
CONNECTING = 'connecting'
START = 'start game'
MOVE = 'move'
DISCONNECT = 'disconnect'
ACK_DISCONNECT = 'acknowledge disconnect'
REJ_DISCONNECT = 'reject disconnect'


class NimPeerNode (Node):


    def __init__(self, host, port, id=None, callback=None, max_connections=0):

        self.game = None # Local game state
        self.myip = host

        # A timer that is set whenever this node is waiting for a message. 
        # It goes off in TURN_TIMEOUT seconds and the node that did not send a message is assumed to have disconnected.
        self.timer = threading.Timer(TURN_TIMEOUT, self.alarm)
        self.timer_start_time = 0
        self.awaited_player = 0

        # Flag that is raised if this node detects a peer failure.
        self.disconnect_detected = False
        self.disconnected_peer = 0

        # Flag that is raised if another node has detected a peer failure and this node is still waiting for a message from that node.
        self.pending_disconnect_alert = False
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

            if data['status'] == CONNECTING:

                self.status_connecting(data)

            elif data['status'] == START and not self.game:

                self.status_start_game(data)
                self.set_timer()

            elif data['status'] == MOVE:

                self.status_move(data)
                self.set_timer()

            elif data['status'] == DISCONNECT:

                # Disconnect alert from another node
                self.status_disconnect(data)

            elif data['status'] == ACK_DISCONNECT:

                # We have reached an agreement, proceed to remove the disconnected peer
                self.remove_peer(data['state'])

            elif data['status'] == REJ_DISCONNECT:

                self.status_reject_disconnect(data)


    """ 
    Handles the initial connecting message.
    We try to connect to the peers.
    """
    def status_connecting(self, data):
        first_peer_ip = data['1']
        second_peer_ip = data['2']
        if self.my_ip == first_peer_ip:
            super(NimPeerNode, self).connect_with_node(second_peer_ip, p2p_port)
            data['status'] = START
            super(NimPeerNode, self).send_to_nodes(data)
    

    """ 
    Let's start the game.
    """
    def status_start_game(self, data):

        # Let's inform the server we are connected to two peers if so
        if len(super(NimPeerNode, self).all_nodes) >= 2:
            print('informing server about two peers')
            self.we_are_connected(data)

        second_peer_ip = data['2']
        # If we are node 2, let's inform node 1 that we can start the game
        if self.my_ip == second_peer_ip:
            super(NimPeerNode, self).send_to_nodes(data)

        # Create the local game state
        if not self.game:
            my_number = self.get_player_number(data)
            self.game = NimGame(self.my_ip, my_number, data['1'], data['2'], data['3'])
            # Decide on an action
            self.action(data)


    """
    What does this function do?
    """
    def we_are_connected(self, data):

        #Connect to json-rpc server
        server_ip = os.getenv("SERVER_IP")
        server = Server('http://' + server_ip + ':' + str(server_port))
        
        # Let's send this message until the server answers it
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
    Decides what to do after our game state has been updated.
    If it is not our turn, we only show the current state.
    If it is our turn:
        1. We show the current state
        2. Make a move (updating our local state again)
        3. Broadcast the new state to others
    TODO: The user has x seconds to make a move. Countdown is displayed to the user.
    """
    def action(self, data):
        self.game.display_game_state()
        if self.game.our_turn():
            updated_state = self.game.make_move()
            data['status'] = MOVE
            data['state'] = updated_state
            super(NimPeerNode, self).send_to_nodes(data)
        

    """
    TODO
    """
    def status_move(self, data):
        # Let's check if we have a pending disconnect alert and reject it
        if self.pending_disconnect_alert == True:
            super(NimPeerNode, self).send_to_nodes(self.create_message(REJ_DISCONNECT, data['state']))

        # Update local game state based on the received message
        self.game.update_state(data['state'])

        # Give some time for the game to update the state. Is this needed?
        time.sleep(1)

        # Decide what to do
        self.action(data)
        

    """
    TODO
    """
    def status_disconnect(self, data):

        disconnected_player = data['state']

        if self.disconnect_detected == True and self.disconnected_peer == disconnected_player:
            # We have also detected this disconnect and awknoledge the alert
            super(NimPeerNode, self).send_to_nodes(self.create_message(ACK_DISCONNECT, disconnected_player))
            # Since we are in an agreement, proceed to remove the disconnected peer
            self.remove_peer(disconnected_player)

        elif self.timer.is_alive() and self.awaited_player == disconnected_player:
            # We are still waiting for an answer from the player
            time_remaining = 20 - (time.time() - self.timer_start_time)
            print("Time remaining in our alarm:",time_remaining)
            self.pending_disconnect_alert = True

        elif self.timer.is_alive() and not self.awaited_player == disconnected_player:
            # We have already received a message from the peer that has been reported
            super(NimPeerNode, self).send_to_nodes(self.create_message(REJ_DISCONNECT, self.game.get_current_state))


    """
    TODO
    """
    def status_reject_disconnect(self, data):
        print("Disconnect was rejected.")
        self.disconnect_detected = False
        self.disconnected_peer = 0
        current_state = data['state']
        if (self.game.get_current_turn_count()) < current_state['turn_count']:
            self.game.update_state(current_state)
            self.action(data)
            self.set_timer()


    """
    TODO
    """
    def create_message(self, status, state = {}):
        data = {}
        data['1'] = self.game.state['players'][0]
        data['2'] = self.game.state['players'][1]
        data['3'] = self.game.state['players'][2]
        data['status'] = status
        data['state'] = state
        return data


    """
    TODO
    """
    def remove_peer(self, disconnected_player):
        self.disconnect_detected = False
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


    # TIMER RELATED FUNCTIONS

    """
    Deletes the previous timer. Creates a new timer.
    """
    def stop_old_timer(self):
        if self.timer.is_alive():
            self.timer.cancel()
            ("Timer stopped.")
            self.timer = threading.Timer(TURN_TIMEOUT, self.alarm)


    """
    Sets the timer.
    """
    def set_timer(self):
        self.stop_old_timer()
        if not self.timer.is_alive():
            self.timer.start()
            self.timer_start_time = time.time()
            self.awaited_player = self.game.get_current_player()


    """
    This function is executed when the alarm goes off.
    """
    def alarm(self):
        disconnected_player = self.game.get_current_player()
        if disconnected_player == self.game.get_my_number(): # For now, we ignore this...
            print("Our own timer for ourselves went off.")
        #First we check if we have a pending disconnect alert
        if self.pending_disconnect_alert == True:
            super(NimPeerNode, self).send_to_nodes(self.create_message(ACK_DISCONNECT, disconnected_player))
            self.remove_peer(disconnected_player)
        # First we raise the disconnect flag
        self.disconnect_detected = True
        self.disconnected_peer = disconnected_player
        # Then we check if the other node agrees about the disconnection
        print("WERE ARE ABOUT TO SEND A DISCONNECT MESSAGE")
        super(NimPeerNode, self).send_to_nodes(self.create_message(DISCONNECT, disconnected_player))


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
