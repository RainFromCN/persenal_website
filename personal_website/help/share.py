import asyncio
import websockets
import json
import threading
import queue


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
msg_que = queue.Queue()

count = 0
mutex = threading.Lock()
online = threading.Semaphore(0)


async def notify_online(meta, num):
    room = meta['room']
    user = meta['user']

    if room in connected_room:
        for remote_user, remote_client in connected_room[room]:
            if remote_user != user:
                await remote_client.send(json.dumps({'online': {'number': f'{num}'}}))


async def handle_entry(meta, socket):
    global count, online
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
    elif len(connected_room[room]) >= 2:
        await socket.send(json.dumps({'reject': {'reason': '该房间人数已满'}}))
        return False
    connected_room[room][user] = socket

    # 必须双方都登录才能发送信息
    mutex.acquire()
    count += 1
    if count == 2:
        await notify_online(meta, 2)
        online.release()
    mutex.release()

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


async def handle_message(websocket, path):
    global count, online, msg_que

    # 检查是否是加入信令
    meta = await websocket.recv() # 接受元信息
    meta = json.loads(meta)
    if 'entry' not in meta:
        await websocket.send(json.dumps({'reject': '通信出错，请退出重进'}))
        return
    
    # 加入房间
    meta = meta['entry']
    if not await handle_entry(meta, websocket):
        return
    
    while True:
        try:
            message = await websocket.recv()

            # 向房间内所有其他用户广播信令
            msg_que.put((meta, message))

        except websockets.exceptions.ConnectionClosed:
            # 连接正常关闭或者异常关闭
            await handle_leave(meta)

            # 当某个人退出的时候，改变信号量
            mutex.acquire()
            count -= 1
            if count == 1:
                await notify_online(meta, 1)
                online.acquire()
            mutex.release()

            break


async def main():
    async with websockets.serve(handle_message, "localhost", 8002):
        await asyncio.Future()  # 保持服务器运行


async def sending_thread():
    global online, msg_que
    while True:
        item = msg_que.get()
        meta, msg = item
        room, user = meta['room'], meta['user']
    
        online.acquire()

        # 向所有用户转发消息
        for other, socket in connected_room[room].items():
            if user != other:
                await socket.send(msg)
        
        online.release()


def share_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


def signal_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(sending_thread())


th1 = threading.Thread(target=signal_server, daemon=True)
th2 = threading.Thread(target=share_server, daemon=True)
th1.start()
th2.start()
