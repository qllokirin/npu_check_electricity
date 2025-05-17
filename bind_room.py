import httpx
import asyncio
import json
import pymsgbox
import time
import sys
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
        print("配置文件已存在✅，开始重新绑定宿舍，绑定完后会覆盖配置文件")
    else:
        print("配置文件不存在，开始绑定宿舍")
    # 选择校区
    msg, campus_all = await get_campus()
    print(msg)
    campus_msg = input("请输入后回车：")
    # 选择楼栋
    campus = campus_all[int(campus_msg)]['value']
    msg, building_all = await get_building(campus)
    print(msg)
    building_msg = input("请输入后回车：")
    # 选择房间
    building = building_all[int(building_msg)]['value']
    msg, room_all = await get_room(campus, building)
    print(msg)
    room_msg = input("请输入后回车：")
    room = room_all[int(room_msg)]['value']
    data = {'campus': campus, 'building': building, 'room': room}
    electric_left, information_all = await get_electric_left(campus, building, room)
    print(f"当前剩余电量：{electric_left}，{information_all}")
    warning_electric = input("请输入电量预警值，直接回车设置为默认值10：")
    if warning_electric == '':
        warning_electric = 10
    else:
        warning_electric = int(warning_electric)
    data = {
        'campus': campus,
        'building': building,
        'room': room,
        'warning_electric': warning_electric
    }
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("配置文件已保存✅")

if __name__ == "__main__":
    asyncio.run(main())