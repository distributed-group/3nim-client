from p2pnetwork.node import Node
from p2pnetwork.nodeconnection import NodeConnection
from NimGame import NimGame
import time
import socket

class NimPeerNode (Node):
    def __init__(self, host, port, id=None, callback=None, max_connections=0):
        self.nimgame = None
        super(NimPeerNode, self).__init__(host, port, id, callback, max_connections)

    def outbound_node_connected(self, connected_node):
        var=0
        #print("outbound_node_connected: " + connected_node.id)
        
    def inbound_node_connected(self, connected_node):
        var=0
        #print("inbound_node_connected: " + connected_node.id)

    def inbound_node_disconnected(self, connected_node):
        var=0
        #print("inbound_node_disconnected: " + connected_node.id)

    def outbound_node_disconnected(self, connected_node):
        var=0
        #print("outbound_node_disconnected: " + connected_node.id)

    def node_message(self, connected_node, data):
        my_ip = socket.gethostbyname(socket.gethostname())
        print("node_message from " + connected_node.host + ": " + str(data))
        #when message arrives, let's answer something
        #super(NimPeerNode, self).send_to_nodes({'msg':'I want to answer to you, I am node with ip ' + my_ip})
        if 'status' in data.keys():
            #if message is initial connecting message, try to connect to two nodes if not yet connected
            if data['status'] == 'connecting':
                second_peer_ip = data['player2']
                first_peer_ip = data['player1']
                #collect connected nodes ip-addresses
                connected_nodes = super(NimPeerNode, self).all_nodes
                conn_hosts = []
                for node in connected_nodes:
                    conn_hosts.append(node.host)
                #try to connect but don't connect if connection exists or if it is myself
                if my_ip != first_peer_ip and first_peer_ip not in conn_hosts:
                    super(NimPeerNode, self).connect_with_node(first_peer_ip, 10001)
                if my_ip != second_peer_ip and second_peer_ip not in conn_hosts:
                    super(NimPeerNode, self).connect_with_node(second_peer_ip, 10001)
                data['status'] = 'start game'
                super(NimPeerNode, self).send_to_nodes(data)
            #if message indicates others are ready, start the game
            elif data['status'] == 'start game' and not self.nimgame:
                self.nimgame = NimGame(my_ip, data['player1'], data['player2'], data['player3'])
                new_state = self.nimgame.turn_manager()
                if new_state:
                    data['status'] = 'move'
                    data['state'] = new_state
                    super(NimPeerNode, self).send_to_nodes(data)
            #if someone has done a move, update game state
            elif data['status'] == 'move':
                self.nimgame.update_state(data['state'])
                #give some thime for the game to update the state
                time.sleep(2) 
                new_state = self.nimgame.turn_manager()
                if new_state:
                    data['status'] = 'move'
                    data['state'] = new_state
                    super(NimPeerNode, self).send_to_nodes(data)
        #time.sleep(10)

        
    def node_disconnect_with_outbound_node(self, connected_node):
        var=0
        #print("node wants to disconnect with oher outbound node: " + connected_node.id)
        
    def node_request_to_stop(self):
        var=0
        #print("node is requested to stop!")

    def create_new_connection(self, connection, id, host, port):
        return NodeConnection(self, connection, id, host, port)
