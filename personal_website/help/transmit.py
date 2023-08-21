import asyncio
import websockets
import json
import threading


from django.shortcuts import render
from django.conf import settings
from .models import User, Cooperation


def transmit(request, room):
    context = {}
    if 'username' in request.session:
        context['usr'] = User.objects.get(name=request.session['username'])
    if 'cooperation' in room:
        c_id = int(room.split('.')[-1])
        context['cooperation'] = Cooperation.objects.get(id=c_id)
    return render(request, "help/transmit.html", context)


connected_user = set()
connected_room = dict()

count = dict()
mutex = dict()


async def notify_online(meta, num, notify_self=False):
    room = meta['room']
    user = meta['user']

    if room in connected_room:
        for remote_user, remote_client in connected_room[room].items():
            if remote_user != user or notify_self:
                await remote_client.send(json.dumps({'notify': {'number': f'{num}'}}))

async def handle_entry(meta, socket):
    global count
    room = meta['room']
    user = meta['user']
    
    # 检查用户是否已经连接
    if user in connected_user:
        await socket.send(json.dumps({'reject': {'reason': '请先退出其他房间后再加入本房间'}}))
        return False
    connected_user.add(user)

    # 将用户加入房间
    if room not in connected_room:
        connected_room[room] = dict()
        count[room] = 0
        mutex[room] = threading.Lock()
    elif len(connected_room[room]) >= 2:
        await socket.send(json.dumps({'reject': {'reason': '该房间人数已满'}}))
        return False
    connected_room[room][user] = socket

    # 通知对方目前房间在线人数
    mutex[room].acquire()
    count[room] += 1
    await notify_online(meta, count[room], notify_self=True)
    mutex[room].release()

    return True


async def handle_leave(meta):

    room = meta['room']
    user = meta['user']

    # 将用户从服务器移除
    if user in connected_user:
        connected_user.remove(user)
    if room in connected_room and user in connected_room[room]:
        del connected_room[room][user]
        if len(connected_room[room]) == 0:
            del connected_room[room]
            del mutex[room]
            del count[room]


async def handle_message(websocket, path):
    global count

    # 检查是否是加入信令
    meta = await websocket.recv() # 接受元信息
    print(meta)

    meta = json.loads(meta)
    if 'entry' not in meta:
        await websocket.send(json.dumps({'reject': '通信出错，请退出重进'}))
        return
    
    # 加入房间
    meta = meta['entry']
    room = meta['room']
    user = meta['user']
    
    if not await handle_entry(meta, websocket):
        print("reject")
        return
    
    while True:
        try:
            message = await websocket.recv()

            # 向房间内所有其他用户广播信令
            for client in (client for u, client in connected_room[room].items() if u != user):
                await client.send(message)

        except websockets.exceptions.ConnectionClosed:
            # 连接正常关闭或者异常关闭
            await handle_leave(meta)

            # 通知其他人目前房间在线人数
            # mutex[room].acquire()
            # count[room] -= 1
            # await notify_online(meta, count[room])
            # mutex[meta[room]].release()

            break


async def main():
    domain = settings.TRANS_SERVER_SITE.split(':')
    async with websockets.serve(handle_message, *domain):
        await asyncio.Future()  # 保持服务器运行


def transmit_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


th = threading.Thread(target=transmit_server, daemon=True)
th.start()
