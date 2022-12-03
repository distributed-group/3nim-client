import sys
import os
import time
import socket
from jsonrpclib import Server
from NimPeerNode import NimPeerNode
from dotenv import load_dotenv

load_dotenv()

my_ip = socket.gethostbyname(socket.gethostname())
p2p_port = 10001
server_port = '5001'
node = NimPeerNode(my_ip, p2p_port)

""" 
Connects this client to the server.
When the client receives 'ready to start' -message, it connects with two peers. 
Peer IP addresses are in the response message.
"""
def connect():
    #Connect to json-rpc server
    server_ip = os.getenv("SERVER_IP")
    server = Server('http://' + server_ip + ':' + server_port)
    try:
        response = server.want_to_play(my_ip)
        print(response)
        if response['status'] == 'ready to start':
            #This node was the third node in the queue and the game can start
            start_game(response)
    except:
        print('Error: ', sys.exc_info())

"""
Connects this client to the peers.
"""
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

if __name__ == '__main__':
    connect()
    node.start()