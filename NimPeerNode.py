import sys
import os
import time
import socket
import threading
from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
from jsonrpclib import Server
from Logger import Logger
from dotenv import load_dotenv

from NimGame import NimGame
import printer


load_dotenv()

p2p_port = 10001
server_port = 5001
TURN_TIMEOUT = 30.0

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

        # A timer that is set whenever this node is waiting for a message from someone.
        # It goes off in TURN_TIMEOUT seconds and the node that did not send a message is assumed to have disconnected.
        self.timer = threading.Timer(TURN_TIMEOUT, self.alarm)
        self.timer_start_time = 0
        self.awaited_player = 0

        # Flag that is raised if this node detects a peer failure.
        self.disconnect_detected = False
        self.disconnected_peer = 0

        # Flag that is raised if another node has detected a peer failure and this node is still waiting for a message from that node.
        self.pending_disconnect_alert = False

        # Log the events.
        self.logger = Logger('log.txt', host)

        super(NimPeerNode, self).__init__(host, port, id, callback, max_connections)


    """
    This function is invoked when another node sends this node a message.
    Based on the message's status code, this function decides what to do next.
    Since all information is communicated through messages, this is the starting point for all actions this node takes.
    """
    def node_message(self, connected_node, data):

        self.my_ip = socket.gethostbyname(socket.gethostname())
        self.logger.write_log('Message from ' + connected_node.host + ': ' + str(data))

        if 'status' in data.keys():

            if data['status'] == CONNECTING:
                
                # Initial p2p-connecting message
                self.status_connecting(data)

            elif data['status'] == START and not self.game:
                
                # Que to start the game
                self.stop_old_timer()
                self.status_start_game(data)
                self.set_new_timer()

            elif data['status'] == MOVE:

                # We have received a move
                self.stop_old_timer()
                if self.status_move(data) == 1:
                    self.set_new_timer() # Game continues
                else:
                    self.shut_down() # Game has ended

            elif data['status'] == DISCONNECT:

                # Disconnect alert from another node
                self.status_disconnect(data)

            elif data['status'] == ACK_DISCONNECT:

                # Our disconnect alert has been accepted and we have reached an agreement. Proceed to remove the disconnected peer and end game.
                self.remove_peer_and_end_game(data['state'])

            elif data['status'] == REJ_DISCONNECT:

                # Our disconnect alert has been rejected, false alarm
                value = self.status_reject_disconnect(data)
                if value == 1:
                    self.set_new_timer() # Game continues
                elif value == 0:
                    self.shut_down() # Game has ended


    """ 
    Handles the 'connecting' -message.
    This message tells node 1 to connect with node 2 and to send the 'start game' -message.
    """
    def status_connecting(self, data):
        first_peer_ip = data['1']
        second_peer_ip = data['2']
        # If we are node 1, connect with node 2 -> all the nodes are then connected
        if self.my_ip == first_peer_ip:
            super(NimPeerNode, self).connect_with_node(second_peer_ip, p2p_port)
            # Send the 'start game' -message to all
            data['status'] = START
            super(NimPeerNode, self).send_to_nodes(data)
    

    """ 
    Handles the 'start game' -message.
    This message tells us all the peer connections have been formed and the game can start.
    """
    def status_start_game(self, data):

        # Let's inform the server we are connected to two peers if so
        if len(super(NimPeerNode, self).all_nodes) >= 2:
            self.logger.write_log('informing server about two peers')
            self.we_are_connected(data)

        second_peer_ip = data['2']
        # If we are node 2, let's inform node 1 that we can start the game
        if self.my_ip == second_peer_ip:
            super(NimPeerNode, self).send_to_nodes(data)

        # Create the local game state
        if not self.game:
            my_number = printer.get_player_number(data, self.my_ip)
            self.game = NimGame(self.my_ip, my_number, data['1'], data['2'], data['3'])
            # Decide on an action
            self.action(data)


    """
    Handles the 'move' -message. 
    This message tells us another player has made a move.
    Return value depends on self.action().
    """
    def status_move(self, data):
        # Let's check if we have a pending disconnect alert and reject it
        if self.pending_disconnect_alert == True:
            super(NimPeerNode, self).send_to_nodes(printer.create_message(self.game, REJ_DISCONNECT, False, data['state']))

        # Update local game state based on the received message and decide what to do (make move or not)
        self.game.update_state(data['state'])
        return self.action(data)


    """
    Handles the 'disconnect' -message.
    This message tells us a peer had detected a disconnected peer.
    """
    def status_disconnect(self, data):

        disconnected_player = data['state']

        if self.disconnect_detected == True and self.disconnected_peer == disconnected_player:
            # We have also detected this disconnect and acknowledge the alert
            super(NimPeerNode, self).send_to_nodes(printer.create_message(self.game, ACK_DISCONNECT, False, disconnected_player))
            # Since we are in an agreement, proceed to remove the disconnected peer and end the game
            self.remove_peer_and_end_game(disconnected_player)

        elif self.timer.is_alive() and self.awaited_player == disconnected_player:
            # We are still waiting for an answer from the player
            time_remaining = TURN_TIMEOUT - (time.time() - self.timer_start_time)
            self.logger.write_log('Time remaining in our alarm: ' + str(time_remaining))
            self.pending_disconnect_alert = True

        elif self.timer.is_alive() and not self.awaited_player == disconnected_player:
            # We have already received a message from the peer that has been reported disconnected. We reject the disconnect alert.
            super(NimPeerNode, self).send_to_nodes(printer.create_message(self.game, REJ_DISCONNECT, False, self.game.get_game_state))


    """
    Handles the 'reject disconnect' -message.
    This message tells us the disconnect we detected was a false alarm.
    If received data is new, return value depends on self.action().
    """
    def status_reject_disconnect(self, data):
        self.logger.write_log('Disconnect was rejected.')
        self.disconnect_detected = False
        self.disconnected_peer = 0
        # We receive the updated game state from the peer that rejected our disconnect message.
        updated_state = data['state']
        # If this is new information to us, update the local game state
        if self.game.get_turn_count() < updated_state['turn_count']:
            self.game.update_state(updated_state)
            return self.action(data)


    """
    Decides what to do after our game state has been updated.
    If it is not our turn, we only show the current game state to the player.
    If it is our turn:
        1. We show the current game state
        2. Make a move (updating and showing our local state again)
        3. Broadcast the move to others
    Returns 0 if the game has ended and 1 otherwise.
    """
    def action(self, data):
        self.game.display_game_state()
        if 'state' in data and data['state']['phase'] == 'ended':
            return 0
        if self.game.our_turn():
            updated_state = self.game.make_move()
            data['status'] = MOVE
            data['state'] = updated_state
            super(NimPeerNode, self).send_to_nodes(data)
            if updated_state['phase'] == 'ended':
                return 0
        return 1


    """
    Moves the disconnected peer to lost players and ends the game. After that shuts this node down.
    If another player has already lost, we announce the remaining player as the winner.
    Otherwise the game ends with no winner.
    """
    def remove_peer_and_end_game(self, disconnected_player):
        self.disconnect_detected = False
        # Add disconnected node to lost players
        self.game.add_player_to_lost(disconnected_player)
        # Disconnect from the disconnected node
        self.disconnect_from_peer(disconnected_player)
        if self.game.is_end(): # Only one player left, so we announce the winner
            # We update our own state
            winner = self.game.find_winner()
            self.game.set_announcement(printer.disconnect_and_winner(disconnected_player, winner))
        else: # The game ends with no winner
            # We update our own state
            self.game.set_phase('ended_no_winner')
            self.game.set_announcement(printer.disconnect(disconnected_player))
        #Show the end screen to player
        self.game.display_game_state()
        self.shut_down()



    # TIMER RELATED FUNCTIONS


    """
    Stops and deletes the previous timer.
    """
    def stop_old_timer(self):
        if self.timer.is_alive():
            self.timer.cancel()
            self.timer = threading.Timer(TURN_TIMEOUT, self.alarm)


    """
    Creates and starts a new timer.
    """
    def set_new_timer(self):
        if not self.timer.is_alive():
            self.timer = threading.Timer(TURN_TIMEOUT, self.alarm)
            self.timer.start()
            self.timer_start_time = time.time()
            self.awaited_player = self.game.get_player_in_turn()


    """
    This function is executed when self.timer goes off.
    """
    def alarm(self):
        #First we check if we have a pending disconnect alert
        if self.pending_disconnect_alert == True:
            super(NimPeerNode, self).send_to_nodes(printer.create_message(self.game, ACK_DISCONNECT, False, self.awaited_player))
            self.remove_peer_and_end_game(self.awaited_player)
        # Then we raise the disconnect flag
        self.disconnect_detected = True
        self.disconnected_peer = self.awaited_player
        # Then we check if the remaining node agrees about the disconnection
        super(NimPeerNode, self).send_to_nodes(printer.create_message(self.game, DISCONNECT, False, self.awaited_player))



    # CONNECTION RELATED FUNCTIONS


    """
    Informs the server that this node has successfully connected to two peers.
    """
    def we_are_connected(self, data):

        #Connect to json-rpc server
        server_ip = os.getenv("SERVER_IP")
        server = Server('http://' + server_ip + ':' + str(server_port))
        
        # Let's send this message until the server answers it
        while True:
            self.logger.write_log('Informing server about the succesful connection with 2 peers')
            try:
                res = server.connected_to_two(data['game_id'], self.my_ip)
                if res['received']:
                    break
            except:
                self.logger.write_log('Error: ' + str(sys.exc_info()))
            time.sleep(2)


    """
    Disconnects this node from a peer. Peer player number is given as a parameter.
    """
    def disconnect_from_peer(self, disconnected_player):
        disconnected_ip = self.game.state['players'][disconnected_player-1]
        self.logger.write_log('disconnected ip is' + str(disconnected_ip))
        self.logger.write_log('disconnected player is ' + str(disconnected_player))
        conn_hosts = []
        for conn in super(NimPeerNode, self).all_nodes:
            conn_hosts.append(conn.host)
            if conn.host == disconnected_ip:
                while len(super(NimPeerNode, self).all_nodes) > 1:
                    super(NimPeerNode, self).disconnect_with_node(conn.stop())
                    time.sleep(5)


    """
    Shuts this node down and logs it.
    """
    def shut_down(self):
        self.logger.write_log('Stop node and shut down program...')
        print('Shutting down...')
        super(NimPeerNode, self).stop()


    # Log other connection activity...


    def outbound_node_connected(self, connected_node):
        self.logger.write_log('outbound_node_connected: ' + str(connected_node.id))
        
    def inbound_node_connected(self, connected_node):
        self.logger.write_log('inbound_node_connected: ' + str(connected_node.id))

    def inbound_node_disconnected(self, connected_node):
        self.logger.write_log('inbound_node_disconnected: ' + str(connected_node.id))

    def outbound_node_disconnected(self, connected_node):
        self.logger.write_log('outbound_node_disconnected: ' + str(connected_node.id))
        
    def node_disconnect_with_outbound_node(self, connected_node):
        self.logger.write_log('node wants to disconnect with oher outbound node: ' + str(connected_node.id))
        
    def node_request_to_stop(self):
        self.logger.write_log('node is requested to stop!')
    