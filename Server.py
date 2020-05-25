import json
from model.grid import Cell
from aiohttp import web
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

def from_json(jsonx):
   pass

def to_json(object):
    return json.dumps(object.from_object_to_dict())

@sio.event
async def connect(sid, environ):
    print('connect ', sid)

@sio.event
async def disconnect(sid):
    print('disconnect ', sid)



@sio.on('message')
async def print_message(sid, message):
    print("Socket ID: ", sid)
    print(message)
    await sio.emit("message", "from server")







if __name__ == '__main__':
    web.run_app(app, host="localhost", port="8080")
