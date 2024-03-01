from redis import Redis
from uuid import uuid4
import json
import asyncio
from fastapi import WebSocket

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
    json_data["options"]["turn_num"] = data["options"]["turn_num"]
    json_data["options"]["discuss_time"] = data["options"]["discuss_time"]
    json_data["options"]["vote_time"] = data["options"]["vote_time"]
    json_data["options"]["participants_num"] = data["options"]["participants_num"]
    
    value = json.dumps(json_data)
    crud.post_redis(redis=redis,key=room_id,value=value)
    return room_id

def _change_room_owner_id(redis: Redis,room_id: str,id: str) -> None:
    value = crud.get_redis(redis=redis,key=room_id)
    value = json.loads(value)
    value["room"]["room_owner_id"] = id
    crud.post_redis(redis=redis,key=room_id,value=json.dumps(value))
    return None

def _get_room_model() -> dict:
    json ={
        "room": {
            "room_id": "",
            "room_owner_id": "",
            "vote_ended": False
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

def _create_response(redis:Redis,event_type: schema.EventTypeEnum,json_data: dict,room_id: str,id: str) -> str:
    match event_type:
        case schema.EventTypeEnum.create_room:
            json_data = _change_create_room_response(redis=redis,json_data=json_data,room_id=room_id)
        case schema.EventTypeEnum.enter_room:
            json_data = _change_enter_room_response(redis=redis,json_data=json_data,room_id=room_id,id=id)
    return json.dumps(json_data)