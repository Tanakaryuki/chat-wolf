from redis import Redis
from uuid import uuid4
import json

import ws.schemas as schema
import ws.cruds as crud

def _create_user(redis: Redis,data: dict,room_id: str) -> str | None:
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
