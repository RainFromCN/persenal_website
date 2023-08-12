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


# SIGNAL_TYPE_JOIN = 'join'
# SIGNAL_TYPE_RESP_JOIN = 'resp-join'
# SIGNAL_TYPE_LEAVE = 'leave'
# SIGNAL_TYPE_NEW_PEER = 'new-peer'
# SIGNAL_TYPE_PEER_LEAVE = 'peer-leave'
# SIGNAL_TYPE_OFFER = 'offer'
# SIGNAL_TYPE_ANSWER = 'answer'
# SIGNAL_TYPE_CANDIDATE = 'candidate'


# # 用于根据不同房间收录 websocket
# room_table_map = dict()

# # 记录当前已经加入房间的用户
# active_users = set()

# # 每次仅允许一个用户进入并连接
# sem = Semaphore(1)


# async def handle_join(msg, ws):
#     room = msg['room']
#     user = msg['from']

#     # 创建房间
#     if room not in room_table_map:
#         room_table_map[room] = dict()

#     # 检查条件
#     cond1 = user in active_users
#     cond2 = len(room_table_map[room]) >= 10
#     agree = False if cond1 or cond2 else True
    
#     # 根据条件设置 reason
#     if cond1:
#         reason = '您已经进入房间，请先退出后再加入其他房间'
#     elif cond2:
#         reason = '该房间已满'
#     else:
#         reason = ''

#     # 设置 others 字段
#     others = list(room_table_map[room].keys())

#     # 需要给信令发送方发送 response join 信令
#     response = {
#         'cmd': SIGNAL_TYPE_RESP_JOIN,
#         'agree': agree,
#         'reason': reason,
#         'others': others
#     }
#     await ws.send(json.dumps(response))

#     if agree is False:
#         # 如果拒绝加入，则直接返回
#         return
#     else:
#         # 将本用户加入房间
#         room_table_map[room][user] = ws
#         active_users.add(user)

#     # 打印日志
#     print(f"{user:20s} 已加入房间 {room:20s} 当前人数 {len(room_table_map[room])}")


# async def handle_leave(msg):
#     room = msg['room']
#     user = msg['from']

#     # 查看条件是否满足
#     cond1 = room not in room_table_map
#     cond2 = user not in room_table_map[room]
#     if cond1 or cond2:
#         return
    
#     # 退出房间
#     del room_table_map[room][user]
#     active_users.remove(user)

#     # 向房间内其他成员发送 peer leave 信令
#     for remote_cilent in room_table_map[room].values():
#         msg = {
#             'cmd': SIGNAL_TYPE_PEER_LEAVE,
#             'from': user,
#             'room': room
#         }
#         await remote_cilent.send(json.dumps(msg))

#     # 打印日志
#     print(f'{user:20s} 已经离房间 {room:20s} 当前人数 {len(room_table_map[room])} 人')

#     # 根据需要删除房间
#     if len(room_table_map[room]) == 0:
#         del room_table_map[room]


# async def handle_offer(msg):
#     room = msg['room']
#     user = msg['from']

#     # 确认用户已经发送过 join 信息
#     cond1 = room not in room_table_map
#     cond2 = user not in room_table_map[room]
#     if cond1 or cond2:
#         return

#     # 向该房间内所有其他用户转发 offer
#     for remote_user, remote_client in room_table_map[room].items():
#         if remote_user == user:
#             continue
#         await remote_client.send(json.dumps(msg))

#     # 打印日志
#     print(f'来自 {user:20s} 的 offer 已经转发给其他所有人')


# async def handle_answer(msg):
#     room = msg['room']
#     user = msg['from']
#     to = msg['to']

#     # 查看answer内容是否合法
#     cond1 = room not in room_table_map
#     cond2 = user not in room_table_map[room]
#     cond3 = to not in room_table_map[room]
#     if cond1 or cond2 or cond3:
#         return

#     # 转发 answer
#     remote_client = room_table_map[room][to]
#     await remote_client.send(json.dumps(msg))

#     # 打印日志
#     print(f'来自 {user:20s} 的 answer 已经转发给 {to:20s}')


# async def handle_candidate(msg):
#     room = msg['room']
#     user = msg['from']

#     # 查看 candidate 内容是否合法
#     cond1 = room not in room_table_map
#     cond2 = user not in room_table_map[room]
#     if cond1 or cond2:
#         return

#     # 转发 candidate
#     for remote_user, remote_client in room_table_map[room].items():
#         if remote_user == user:
#             continue
#         await remote_client.send(json.dumps(msg))

#     # 打印日志
#     print(f'来自 {user:20s} 的 candidate 已经转发房间内其他人')


socket_set = set()

async def handle_message(websocket, path):
    # # 新的连接建立
    # meta = await websocket.recv() # 接受元信息
    # meta = json.loads(meta)
    # if meta['cmd'] != SIGNAL_TYPE_JOIN:
    #     return

    # # 建立连接，加入房间
    # await handle_join(meta, websocket)

    socket_set.add(websocket)
    
    while True:
        try:
            message = await websocket.recv()
            if len(socket_set == 1):
                # 目前没有人，先暂存消息

            for socket in socket_set:
                if socket is not websocket:
                    await socket.send(message)
            # # 接受到信息
            # message = await websocket.recv()
            # message = json.loads(message)

            # if message['cmd'] == SIGNAL_TYPE_OFFER:
            #     await handle_offer(message)
            # elif message['cmd'] == SIGNAL_TYPE_ANSWER:
            #     await handle_answer(message)
            # elif message['cmd'] == SIGNAL_TYPE_CANDIDATE:
            #     await handle_candidate(message)

        except websockets.exceptions.ConnectionClosed:
            # 连接正常关闭或者异常关闭
            # await handle_leave(meta)
            socket_set.remove(websocket)
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
