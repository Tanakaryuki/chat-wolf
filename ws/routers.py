from fastapi import APIRouter, Depends
from redis import Redis

import ws.schemas as schema
import ws.cruds as cruds
from ws.redis import get_redis

router = APIRouter()

@router.post("/redis/get", response_model=schema.RedisGetResponse)
async def get_redis_list(request: schema.RedisGetRequest,redis: Redis = Depends(get_redis)):
    value=cruds.get_redis(redis=redis,key=request.key)
    if value:
        return schema.RedisGetResponse(value=value)
    else:
        return schema.RedisGetResponse(value=None)

@router.post("/redis/post", response_model=schema.RedisInsertResponse)
async def get_redis_list(request: schema.RedisInsertRequest,redis: Redis = Depends(get_redis)):
    cruds.post_redis(redis=redis,key=request.key,value=request.value)
    return schema.RedisInsertResponse(key=request.key, value=request.value)

@router.post("/redis/list", response_model=schema.RedisGetListResponse)
async def get_redis_list(redis: Redis = Depends(get_redis)):
    items = cruds.get_redis_list(redis=redis)
    return schema.RedisGetListResponse(items=items)