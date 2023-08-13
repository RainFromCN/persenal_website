import asyncio
import websockets
import json
import logging
import threading


from django.shortcuts import render
from .models import User, Cooperation


def share(request, room):
    context = {}
    if 'username' in request.session:
        context['usr'] = User.objects.get(name=request.session['username'])
    if 'cooperation' in room:
        c_id = int(room.split('.')[-1])
        context['cooperation'] = Cooperation.objects.get(id=c_id)
    return render(request, "help/share.html", context)


connected_user = set()
connected_room = dict()


async def handle_entry(meta, socket):
    
    # 检查用户是否已经连接
    if meta['user'] in connected_user:
        print('reject')
        await socket.send(json.dumps({'reject': {'reason': '请先退出其他房间后再加入本房间'}}))
        return False
    connected_user.add(meta['user'])

    # 将用户加入房间
    if meta['room'] not in connected_room:
        connected_room['room'] = dict()
    elif len(connected_room[meta['room']]) >= 2:
        await socket.send(json.dumps({'reject': {'reason': '该房间人数已满'}}))
        return False
    connected_room['room']['user'] = meta['user']

    return True


async def handle_leave(meta):

    # 将用户从服务器移除
    if meta['user'] in connected_user:
        connected_user.remove(meta['user'])
    if meta['room'] in connected_room and meta['user'] in connected_room[meta['room']]:
        del connected_room[meta['room']][meta['user']]
        if len(connected_room[meta['room']]) == 0:
            del connected_room[meta['room']]


async def handle_message(websocket, path):

    # 检查是否是加入信令
    meta = await websocket.recv() # 接受元信息
    meta = json.loads(meta)
    if 'entry' not in meta:
        await socket.send(json.dumps({'reject': '通信出错，请退出重进'}))
        return
    
    # 加入房间
    meta = meta['entry']
    if not await handle_entry(meta, websocket):
        return
    
    while True:
        try:
            message = await websocket.recv()

            # 向房间内所有其他用户广播信令
            for user, socket in connected_room[meta['room']].items():
                if user != meta['user']:
                    await socket.send(message)

        except websockets.exceptions.ConnectionClosed:
            # 连接正常关闭或者异常关闭
            await handle_leave(meta)
            break


async def main():
    async with websockets.serve(handle_message, "localhost", 8002):
        await asyncio.Future()  # 保持服务器运行


def chat_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


import threading
th = threading.Thread(target=chat_server, daemon=True)
th.start()
