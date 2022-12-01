from jsonrpclib import Server
import sys, socket, time
from jsonrpcserver import method, Success, Result, Error, InvalidParams, async_dispatch
import websockets
import asyncio
import re
import logging
from jsonrpcclient import Ok, parse_json, request_json



async def start_game(players, my_ip):
	#connect with player number 1
	first_peer_ip = players['player1']
	second_peer_ip = players['player2']
	async with websockets.connect('ws://'+first_peer_ip+':5002') as ws:        
		req = request_json('greet', {"message": 'Hello, I connected with you, my ip is ' + my_ip})
		await ws.send(req)
		result = await ws.recv()
		response = parse_json(result)    
	if isinstance(response, Ok):
		print(response.result)
	else:        
		logging.error(response.message)

@method
async def greet(message) -> Result:
    result = { "message": message, "result" : "Nice to hear you!" }
    return Success(result)

async def start_socket(websocket, path):
    if response := await async_dispatch(await websocket.recv()):
        await websocket.send(response)

def connect():
	server_ip = '192.168.10.5' #fill correct server ip here
	my_ip = socket.gethostbyname(socket.gethostname())
	server = Server('http://' +server_ip+ ':5001')
	try:
		response = server.want_to_play(my_ip)
		print(response)
		if response['status'] != 'wait for players':
			asyncio.get_event_loop().run_until_complete(start_game(response, my_ip))		
			#start_game_task = asyncio.create_task(start_game(response, my_ip))
			#await start_game_task
		#start a websocket in port 5002 in own ip adress
		start_server = websockets.serve(start_socket, my_ip, 5002)
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()
	except:
		print('Error: ', sys.exc_info())

	

      
if __name__ == '__main__':
	connect()

