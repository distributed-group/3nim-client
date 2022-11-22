from jsonrpclib import Server
import sys, socket

def main():
	server = Server('http://192.168.10.5:5001')
	try:
		print(server.want_to_play(socket.gethostbyname(socket.gethostname())))
	except:
		print('Error: ', sys.exc_info())
		
if __name__ == '__main__':
	main()

