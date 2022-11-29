import sys
import time
import socket
from jsonrpclib import Server
from NimPeerNode import NimPeerNode

my_ip = socket.gethostbyname(socket.gethostname())
node = NimPeerNode(socket.gethostbyname(socket.gethostname()), 10001)


def connect():
    #connect to json-rpc server
    server_ip = '192.168.10.5' #fill correct server ip here
    server = Server('http://' +server_ip+ ':5001')
    try:
        response = server.want_to_play(my_ip)
        print(response)
        if response['status'] == 'ready to start':
            #this means this node was the third node in the queue and game can start
            start_game(response)
    except:
        print('Error: ', sys.exc_info())

def start_game(peer_ips):
    first_peer_ip = peer_ips['player1']
    second_peer_ip = peer_ips['player2']

    #connect with the other two nodes, 1 and 2
    node.connect_with_node(first_peer_ip, 10001)
    node.connect_with_node(second_peer_ip, 10001)
    time.sleep(2)

    #send the ip addresses to nodes 1 and 2 so they can reach each others
    peer_ips['status'] = 'connecting'
    node.send_to_nodes(peer_ips)

    time.sleep(20) #now hang out 20secs to see if there are messages passed between all nodes

    node.stop()

if __name__ == '__main__':
    connect()
    node.start()