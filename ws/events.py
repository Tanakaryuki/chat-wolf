from redis import Redis
from uuid import uuid4
import json
from fastapi import WebSocket
import random

import ws.schemas as schema
import ws.cruds as crud

room_users: dict[str, list[WebSocket]] = {}

def _create_user(redis: Redis,data: dict,room_id: str) -> str:
    value = crud.get_redis(redis=redis,key=room_id)
    value = json.loads(value)
    
    id = str(uuid4())
    value["users"].append({
        "id": id,
        "display_name": data["user"]["display_name"],
        "icon": data["user"]["icon"],
        "is_wolf": False,
        "score": 0,
        "word": "",
        "is_participant": True,
        "vote": {
            "id": "",
            "display_name": ""
        }
    })
    crud.post_redis(redis=redis,key=room_id,value=json.dumps(value))
    return id
    
def _create_room(redis: Redis,data: dict) -> str | None:
    json_data = _get_room_model()
    room_id = str(uuid4())
    json_data["room"]["room_id"] = room_id
    json_data["options"]["turn_num"] = int(data["options"]["turn_num"])
    json_data["options"]["discuss_time"] = int(data["options"]["discuss_time"])
    json_data["options"]["vote_time"] = int(data["options"]["vote_time"])
    json_data["options"]["participants_num"] = int(data["options"]["participants_num"])
    
    value = json.dumps(json_data)
    crud.post_redis(redis=redis,key=room_id,value=value)
    return room_id

def _change_room_owner_id(redis: Redis,room_id: str,id: str) -> None:
    value = crud.get_redis(redis=redis,key=room_id)
    value = json.loads(value)
    value["room"]["room_owner_id"] = id
    crud.post_redis(redis=redis,key=room_id,value=json.dumps(value))
    return None

def _change_room_mode(redis: Redis,room_id: str,mode: str,json_data: dict) -> None:
    value = crud.get_redis(redis=redis,key=room_id)
    value = json.loads(value)
    value["status"]["mode"] = mode
    value["vote_ended"] = False
    value["options"]["turn_num"] = int(json_data["options"]["turn_num"])
    value["options"]["discuss_time"] = int(json_data["options"]["discuss_time"])
    value["options"]["vote_time"] = int(json_data["options"]["vote_time"])
    value["options"]["participants_num"] = int(json_data["options"]["participants_num"])
    num = len(value["users"])
    if mode == "question":
        value["status"]["turn_now"] = 0
        wolf = random.choice([0,num - 1])
        value["room"]["wolf"] = wolf
        for i in range(num):
            if i == wolf:
                value["users"][i]["is_wolf"] = True
                value["users"][i]["word"] = "apple"
            else:
                value["users"][i]["is_wolf"] = False
                value["users"][i]["word"] = "banana"
    
    crud.post_redis(redis=redis,key=room_id,value=json.dumps(value))
    return None

async def _give_word(redis: Redis,room_id: str,json_data: dict) -> None:
    global room_users
    num = 0
    for user in room_users[room_id]:
        message = _create_response(redis=redis, event_type=schema.EventTypeEnum.start_game, json_data=json_data, room_id=room_id, id="", num=num)
        num += 1
        await user.send_text(message)

def _get_room_model() -> dict:
    json ={
        "room": {
            "room_id": "",
            "room_owner_id": "",
            "vote_ended": False,
            "wolf": -1
        },
        "options": {
            "turn_num": 0,
            "discuss_time": 0,
            "vote_time": 0,
            "participants_num": 0
        },
        "status": {
            "mode": "wait",
            "turn_now": "",
        },
        "time_now": "",
        "win": None,
        "users": []
    }
    return json

async def _broadcast(room_id: str,message: str) -> None:
    global room_users
    for user in room_users[room_id]:
        await user.send_text(message)
        
def _change_create_room_response(redis:Redis,json_data: dict,room_id: str) -> dict:
    value = crud.get_redis(redis=redis,key=room_id)
    value = json.loads(value)
    json_data["user"]["id"] = value["users"][0]["id"]
    json_data["room"] = {
        "room_id": room_id,
        "room_owner_id": value["users"][0]["id"]
    }
    
    return json_data
        
def _change_enter_room_response(redis:Redis,json_data: dict,room_id: str,id: str) -> dict:
    value = crud.get_redis(redis=redis,key=room_id)
    value = json.loads(value)
    json_data["user"]["id"] = id
    json_data["users"] = value["users"]
    
    return json_data

def _change_start_game_response(redis:Redis,json_data: dict,room_id: str,id: str,num: int) -> dict:
    value = crud.get_redis(redis=redis,key=room_id)
    value = json.loads(value)
    json_data["user"]["word"] = value["users"][num]["word"]
    
    return json_data

def _change_enter_room_broadcast(redis:Redis,json_data: dict,room_id: str,id: str) -> dict:
    value = crud.get_redis(redis=redis,key=room_id)
    value = json.loads(value)
    json_data["user"]["id"] = id
    json_data["users"] = value["users"]
    
    return json_data

def _change_start_game_broadcast(redis:Redis,json_data: dict,room_id: str,id: str) -> dict:
    json_data["options"]["turn_num"] = int(json_data["options"]["turn_num"])
    json_data["options"]["discuss_time"] = int(json_data["options"]["discuss_time"])
    json_data["options"]["vote_time"] = int(json_data["options"]["vote_time"])
    json_data["options"]["participants_num"] = int(json_data["options"]["participants_num"])
    
    return json_data

def _create_response(redis:Redis,event_type: schema.EventTypeEnum,json_data: dict,room_id: str,id: str,num: int|None) -> str:
    match event_type:
        case schema.EventTypeEnum.create_room:
            json_data = _change_create_room_response(redis=redis,json_data=json_data,room_id=room_id)
        case schema.EventTypeEnum.enter_room:
            json_data = _change_enter_room_response(redis=redis,json_data=json_data,room_id=room_id,id=id)
        case schema.EventTypeEnum.start_game:
            json_data = _change_start_game_response(redis=redis,json_data=json_data,room_id=room_id,id=id,num=num)
    return json.dumps(json_data)

def _create_broadcast(redis:Redis,event_type: schema.EventTypeEnum,json_data: dict,room_id: str,id: str) -> str:
    match event_type:
        case schema.EventTypeEnum.enter_room:
            json_data = _change_enter_room_broadcast(redis=redis,json_data=json_data,room_id=room_id,id=id)
        case schema.EventTypeEnum.start_game:
            json_data = _change_start_game_broadcast(redis=redis,json_data=json_data,room_id=room_id,id=id)
    return json.dumps(json_data)