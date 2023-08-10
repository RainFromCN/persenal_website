from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import asyncio
import websockets
import json


# 用于记录已经登录的
connected_clients = dict()
# 聊天缓存
chat_cache = dict()


@csrf_exempt
def get_chat_msgs(request):
    c_id = int(request.POST.get('cooperation_id'))
    if c_id in chat_cache:
        chat_msgs = chat_cache[c_id]
        return JsonResponse({'chat_msgs': chat_msgs})
    else:
        return JsonResponse({})
    

@csrf_exempt
def remove_chat_msgs(request):
    c_id = int(request.POST.get('cooperation_id'))
    if c_id in chat_cache:
        del chat_cache[c_id]
    return JsonResponse({})


def _msg(username: str, msg: str, login=False, logout=False, online=False):
    return json.dumps({
        'data': {
            'username': username,
            'msg': msg,
            'login': login,
            'logout': logout,
            'online': online,
        }
    })


async def _broadcast(c_id: int, msg):
    if c_id in connected_clients:
        for client in connected_clients[c_id]:
            await client.send(msg)


async def handle_message(websocket, path):
    # 新的连接建立时
    meta = json.loads(await websocket.recv())
    if (c_id := int(meta['cooperation_id'])) in connected_clients:
        connected_clients[c_id].add(websocket)
        await _broadcast(c_id, _msg(meta['username'], '我已上线', login=True, online=True))
    else:
        connected_clients[c_id] = {websocket}
    print(f"合作 {len(connected_clients)}\t 用户 {sum([len(x) for x in connected_clients.values()])}\t {meta['username']}加入")

    while True:
        try:
            # 接受到信息时
            message = await websocket.recv()

            # 缓存信息
            if c_id not in chat_cache:
                chat_cache[c_id] = list()
            chat_cache[c_id].append({
                'username': meta['username'],
                'msg': f"{message}",
            })
            while len(chat_cache[c_id]) > 100:
                chat_cache[c_id].pop(0)
            
            # 返回响应数据
            response = _msg(meta['username'], f"{message}")
            await _broadcast(c_id, response)

        except websockets.exceptions.ConnectionClosed:
            # 连接关闭时
            connected_clients[c_id].remove(websocket)
            if len(connected_clients[c_id]) > 0:
                response = _msg(meta['username'], '我已离开', logout=True)
                await _broadcast(c_id, response)
            else:
                del connected_clients[c_id]
            print(f"合作 {len(connected_clients)}\t 用户 {sum([len(x) for x in connected_clients.values()])}\t {meta['username']}离开")
            break


async def main():
    async with websockets.serve(handle_message, "localhost", 8001):
        await asyncio.Future()  # 保持服务器运行


def chat_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


import threading
th = threading.Thread(target=chat_server, daemon=True)
th.start()
