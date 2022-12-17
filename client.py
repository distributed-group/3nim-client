import sys
import os
import time
import socket
import threading
from Logger import Logger
from jsonrpclib import Server
from NimPeerNode import NimPeerNode
from dotenv import load_dotenv


load_dotenv()

DISCONNECT_TIMEOUT = 10.0
my_ip = socket.gethostbyname(socket.gethostname())
p2p_port = 10001
server_port = 5001
node = NimPeerNode(my_ip, p2p_port)
timer_running = False
logger = Logger('log.txt', my_ip)


""" 
Connects this client to the server.
When the client receives 'ready to start' -message, it starts connecting with peers. 
Peer IP addresses are in the response message.
"""
def connect():
    global timer_running
    # Connect to json-rpc server
    server_ip = os.getenv("SERVER_IP")
    server = Server('http://' + server_ip + ':' + str(server_port))
    try:
        response = server.want_to_play(my_ip)
        print(response['status'])
        if response['status'] == 'Waiting for players...':
            logger.write_log('game_id when waiting ' + str(response['game_id']))
            while True:
                res = server.is_connecting_started(response['game_id'])
                if res['connecting_started']:
                    logger.write_log('connecting started')
                    break
                time.sleep(1)
            print('Started to establish peer connections')
            timer = threading.Timer(DISCONNECT_TIMEOUT, alarm)
            timer.start()
        elif response['status'] == 'ready to start':
            # This node was the third node in the queue and the game can start
            # Third node has its own timer alarm
            timer = threading.Timer(DISCONNECT_TIMEOUT, alarm_node3)
            timer.start()
            start_game(response)
        # Check constantly from the server if the peer connections are established within the time limit of the timer
        timer_running = True
        logger.write_log('game_id when checking connection ' + str(response['game_id']))
        connecter = threading.Thread(target=check_connection, args=(response['game_id'], server, timer, logger), daemon=True)
        connecter.start()
    except:
        print('Error: ', sys.exc_info())
        logger.write_log('Error: '+ str(sys.exc_info()))


"""
Polling the server and asking if peer connections are established succesfully.
Uses timer's time limit. This function stops if time limit is reached.
"""
def check_connection(game_id, server, timer, logger):
    global timer_running
    print('Connecting...')
    logger.write_log('Connecting to peers...')
    while timer_running:
        time.sleep(1)
        # During countdown, check if the connection is succesful. If yes, shut down the timer.
        res = server.are_we_connected(game_id)
        if res['connected']:
            logger.write_log('Connected!')
            timer.cancel()
            break


"""
This is called when the timer runs out of time.
Node breaks the peer connections, if any, and goes back to the server's queue.
"""
def alarm():
    global timer_running
    timer_running = False
    print('Failed to connect with peers. Going back to queue, waiting for new players to play with.')
    logger.write_log('Failed to connect with peers.')
    disconnect_from_nodes()
    connect()


"""
This is called when third node's timer runs out of time.
Node breaks connections to peers, if any, and shuts down.
"""
def alarm_node3():
    global timer_running
    timer_running = False
    print('Failed to connect with peers.')
    logger.write_log('Failed to connect with peers.')
    disconnect_from_nodes()
    print('Shutting down node.')
    logger.write_log('Shutting down node.')
    node.stop()


"""
Disconnects the node from all it's peers.
"""
def disconnect_from_nodes():
    logger.write_log('Disconnecting with nodes ' + str(node.all_nodes))
    while len(node.nodes_outbound + node.nodes_inbound) > 0:
        for n in (node.nodes_outbound + node.nodes_inbound):
            node.disconnect_with_node(n.stop())
        time.sleep(5)


"""
Connects this node to the peers.
This code is executed by node 3.
"""
def start_game(peer_ips):

    first_peer_ip = peer_ips['1']
    second_peer_ip = peer_ips['2']

    # Connect with the other two nodes, 1 and 2
    node.connect_with_node(first_peer_ip, p2p_port)
    node.connect_with_node(second_peer_ip, p2p_port)
    time.sleep(2)

    # Share the IP addresses to nodes 1 and 2 so they can reach each other
    peer_ips['status'] = 'connecting'
    node.send_to_nodes(peer_ips)
    logger.write_log('Connecting message and IPs sent to nodes 1 and 2')


"""
Clears the terminal.
"""
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':
    clear()
    connect()
    node.start()