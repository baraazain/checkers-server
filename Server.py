from model import utils
from model.actors import RandomAgent

from aiohttp import web
import socketio

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)


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


@sio.on('get_player')
async def fuck(sid,message):
    print("Socket ID: ", sid)
    print(message)
    player = RandomAgent(2,"random",123456,1600)
    await sio.emit("get_player",{
        "data": utils.to_json(player),
        "ababa": "ababa",

    })






if __name__ == '__main__':
    web.run_app(app, host="localhost", port="8080")
