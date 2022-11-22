from jsonrpclib import Server
import sys, socket, time
from jsonrpcserver import method, Success, Result, Error, InvalidParams, async_dispatch
import websockets
import asyncio
import re
import logging
from jsonrpcclient import Ok, parse_json, request_json



async def start_game(players):
	async with websockets.connect("ws://"+players['player2']+":5002") as ws:        
		req = request_json("validZipCode", {"zip":"12345"})
		print(req) 
		await ws.send(req)
		result = await ws.recv()
		print(result)  
		response = parse_json(result)    
	if isinstance(response, Ok):
		print(response.result)
	else:        
		logging.error(response.message)

@method
async def validZipCode(zip) -> Result:
    if zip == "":
        return InvalidParams("Null value")
    if re.match("^[0-9]{5}(?:-[0-9]{4})?$", zip):
        result = { "zip": zip, "result" : "Valid Zipcode" }
    else:
        result = { "zip": zip, "result" : "Invalid Zipcode" }
    return Success(result)

async def start_socket(websocket, path):
    if response := await async_dispatch(await websocket.recv()):
        await websocket.send(response)
        
def connect():
	server = Server('http://192.168.10.5:5001')
	try:
		response = server.want_to_play(socket.gethostbyname(socket.gethostname()))
		if response['status'] != 'wait for players':
			asyncio.get_event_loop().run_until_complete(start_game(response))		
		start_server = websockets.serve(start_socket, socket.gethostbyname(socket.gethostname()), 5002)
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()
	except:
		print('Error: ', sys.exc_info())

	

      
if __name__ == '__main__':
	connect()

