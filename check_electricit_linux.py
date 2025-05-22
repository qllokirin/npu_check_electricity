import httpx
import asyncio
import json
import time
import sys
import requests
from datetime import datetime
from pathlib import Path

url = "https://yktapp.nwpu.edu.cn/jfdt/charge/feeitem/getThirdData"

async def get_campus():
    data = {'feeitemid': '182', 'type': 'select', 'level': '0'}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=url,
            data=data
        )
        campus_all = response.json()['map']['data']
        msg = ""
        for i, campus in enumerate(campus_all):
            msg += str(i) + '  ' + campus['name'] + '\n'
        msg += '选择校区，如0或1'
        return msg, campus_all

async def get_building(campus):
    data = {'feeitemid': '182', 'type': 'select', 'level': '1', 'campus': campus}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=url,
            data=data
        )
        building_all = response.json()['map']['data']
        msg = ""
        for i, building in enumerate(building_all):
            msg += str(i) + '  ' + building['name'] + '\n'
        msg += '选择楼栋，如0或1'
        return msg, building_all

async def get_room(campus, building):
    data = {'feeitemid': '182', 'type': 'select', 'level': '2', 'campus': campus, 'building': building}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=url,
            data=data
        )
        room_all = response.json()['map']['data']
        msg = ""
        for i, building in enumerate(room_all):
            msg += str(i) + '  ' + building['name'] + '\n'
        msg += '选择房间，如0或1'
        return msg, room_all

async def get_electric_left(campus, building, room):
    data = {'feeitemid': '182', 'type': 'IEC', 'level': '3', 'campus': campus, 'building': building, 'room': room}
    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, data=data)
        result = response.json()['map']
        return float(result['showData']['当前剩余电量']), f"{result['data']['campus']} {result['data']['building']} {result['data']['room']}"

async def check_network():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("https://yktapp.nwpu.edu.cn/jfdt/charge/feeitem/getThirdData")
            return response.status_code == 200
    except Exception as e:
        print(f"发生错误：{e}")
        return False


def send_private_msg(msg, user_id):
    headers = {
        "Authorization": ""
    }
    data = {
        "user_id": user_id,
        "message": [
            {
                "type": "text",
                "data": {
                    "text": msg
                }
            }
        ]
    }
    response = requests.post('http://127.0.0.1:3000/send_private_msg', headers=headers, json=data)
    print(response.text)

def send_msg(msg, group_id):
    url = "http://127.0.0.1:3000/send_group_msg"
    data = {
        "group_id": group_id,
        "message": [
            {
                "type": "text",
                "data": {
                    "text": msg
                }
            }
        ]
    }
    headers = {
        "Authorization": "",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=data, headers=headers)
    print(response.text)
async def main():
    timeout_time = 120
    start_time = time.time()
    while True:
        if time.time() - start_time > timeout_time:
            print("超时，程序结束")
            return
        if await check_network():
            print("网络连接正常✅")
            break
        else:
            print("网络连接失败，5s后重试")
            await asyncio.sleep(5)
            
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
    else:
        exe_dir = Path(__file__).parent
    file_path = exe_dir / 'check_electricity.json'
    if file_path.exists():
        print("配置文件已存在✅，正在读取配置文件，自动查询电量")
        data = json.loads(file_path.read_text(encoding='utf-8'))
        electric_left, information_all = await get_electric_left(data['campus'], data['building'], data['room'])
        print("当前时间是：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(f"当前剩余电量：{electric_left}，{information_all}")
        with open(exe_dir / 'info.log', 'a', encoding='utf-8') as f:
            f.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {electric_left}，{information_all}\n')
        if electric_left < data['warning_electric']:
            print("电量不足，请及时充值")
            if 'user_id' in data:
                send_private_msg(f"电量不足，请及时充值，当前剩余电量：{electric_left}，{information_all}", data['user_id'])
            if 'group_id' in data:
                send_msg(f"电量不足，请及时充值，当前剩余电量：{electric_left}，{information_all}", data['group_id'])
    else:
        print("配置文件不存在，请执行bind_room进行绑定")
if __name__ == "__main__":
    asyncio.run(main())