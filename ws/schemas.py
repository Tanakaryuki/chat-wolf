from enum import Enum
from pydantic import BaseModel,Field

class EventTypeEnum(str, Enum):
    create_room = "create_room"
    enter_room = "enter_room"
    start_game = "start_game"

class VoteItem(BaseModel):
    id: str | None
    display_name: str | None

class UserItem(BaseModel):
    id: str | None
    display_name: str | None
    icon: str | None
    is_wolf: bool | None
    score: int | None
    word: str | None
    is_participant: bool | None
    vote: VoteItem | None
    
class RoomItem(BaseModel):
    room_id: str | None
    room_owner_id: str | None
    vote_ended: bool | None

class OptionItem(BaseModel):
    turn_num: int | None
    discuss_time: int | None
    vote_time: int | None
    participants_num: int | None
    
class WinEnum(str, Enum):
    wolf = "wolf"
    citizen = "citizen"
    draw = "draw"
    
class UsersItem(BaseModel):
    display_name: str | None
    is_wolf: bool | None
    score: int | None
    word: str | None
    vote: list[VoteItem] | None

class Request(BaseModel):
    event_type: EventTypeEnum
    user: UserItem | None
    room: RoomItem | None
    chat_text: str | None
    options: OptionItem | None
    time_now: str | None
    win: WinEnum | None
    users: list[UsersItem] | None
    
class Response(BaseModel):
    event_type: EventTypeEnum
    user: UserItem | None
    room: RoomItem | None
    chat_text: str | None
    options: OptionItem | None
    time_now: str | None
    win: WinEnum | None
    users: list[UsersItem] | None
    
class RedisGetRequest(BaseModel):
    key: str

class RedisInsertRequest(BaseModel):
    key: str
    value: str
    
class RedisGetResponse(BaseModel):
    value: str | None
    
class RedisInsertResponse(BaseModel):
    key: str | None

class RedisGetListResponse(BaseModel):
    items: list[tuple[str, str]] | None

class ModeTypeEnum(str, Enum):
    wait = "wait"
    question = "question"
    voting = "voting"

class status(BaseModel):
    mode: ModeTypeEnum
    turn_now: str | None

class RoomModel(BaseModel):
    room: RoomItem | None
    options: OptionItem | None
    status: status | None
    time_now: str | None
    win: WinEnum | None
    users: list[UserItem|None] | None