import sys
import os
import time
import socket
from jsonrpclib import Server
from NimPeerNode import NimPeerNode
from dotenv import load_dotenv
import threading

class check_connection(threading.Thread):
    def __init__(self, response, server, timer):
        threading.Thread.__init__(self)
        self.daemon = True
        self.response = response
        self.server = server
        self.timer = timer
        self.start()
    def run(self):
        while timer_running:
            time.sleep(2)
            print('connecting...')
            # During countdown, check if the connection is succesful, if yes, shut down timer
            res = self.server.are_we_connected(self.response['game_id'])
            if res['connected']:
                print('Connected!')
                self.timer.cancel()
                break

load_dotenv()

DISCONNECT_TIMEOUT = 10.0
my_ip = socket.gethostbyname(socket.gethostname())
p2p_port = 10001
server_port = 5001
node = NimPeerNode(my_ip, p2p_port)
attempt = 0
attempt_is_connected = 0
connecter = None
timer_running = False

""" 
Connects this client to the server.
When the client receives 'ready to start' -message, it connects with two peers. 
Peer IP addresses are in the response message.
"""
def connect():
    global attempt, attempt_is_connected, connecter, timer_running
    attempt = attempt + 1
    #Connect to json-rpc server
    server_ip = os.getenv("SERVER_IP")
    server = Server('http://' + server_ip + ':' + str(server_port))
    try:
        response = server.want_to_play(my_ip)
        print(response['status'])
        if response['status'] == 'Waiting for players...':
            print('game_id when waiting', response['game_id'])
            while True:
                time.sleep(5)
                res = server.is_connecting_started(response['game_id'])
                print('.')
                if res['connecting_started']:
                    print('connection started')
                    break
            print('started to establish peer connections')
            # Here we could start countdown, if the game does not start, go back to queue
            timer = threading.Timer(DISCONNECT_TIMEOUT, alarm)
            timer.start()
            timer_running = True
            attempt_is_connected = attempt_is_connected + 1
            print('game_id when checking connection', response['game_id'])
            if attempt == attempt_is_connected:
                connecter = check_connection(response, server, timer)
            else:
                print('Non matching attempts', attempt,' inloop ',  attempt_is_connected)
        elif response['status'] == 'ready to start':
            #This node was the third node in the queue and the game can start
            print('3node game id', response['game_id'])
            start_game(response)
    except:
        print('Error: ', sys.exc_info())

"""
This is calld when timer runs out of time
"""
def alarm():
    global timer_running
    timer_running = False
    print('Failed to connect with peers. Going back to queue, waiting for new players to play with.')
    for n in node.all_nodes:
        node.disconnect_with_node(n)
    connect()


"""
Connects this client to the peers.
This code is executed by node 3.
"""
def start_game(peer_ips):
    first_peer_ip = peer_ips['1']
    second_peer_ip = peer_ips['2']

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