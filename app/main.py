from starlette.responses import JSONResponse
from pydantic import BaseModel

from app.services.finding_matching_mkeywords import moodKeywords_sentence_to_our_keywords
from app.services.tockenizing_foodcategory import tockenizing_foodcategory
from app.services.recommnad_one import restaurants_for_one
from app.services.recommnad_two_sklearn import restaurants_for_many, get_rest_within_onek_from_redis
from app.services.restaurants_within_onek import api_restaurants_within_onek
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient, UpdateOne
import requests

app = FastAPI()
client = MongoClient(
        'mongodb+srv://jiyoung:jiyoung1234^^@favsniper.gg9uyie.mongodb.net/?retryWrites=true&w=majority')
db = client["sniper"]
collection = db["user_csv"]

# 사용자 장소 반경 1km내 식당 리스트
class Restaurants_within_onek(BaseModel):
    userId: str
    base_coords: list


@app.post("/restaurants/withinonek")
async def restaurants_within_onek(restaurants_within_onek: Restaurants_within_onek):
    try:
        rest_id_list, num_res_within_onek = api_restaurants_within_onek(
            restaurants_within_onek)  # nearby_restaurants 변수 추가
        #insert_restaurants(nearby_restaurants)  # nearby_restaurants를 insert_restaurants 함수에 전달
        return JSONResponse(content={"userId": restaurants_within_onek.userId,
                                     "restaurant_id_list": rest_id_list,
                                     "num_res_within_onek": num_res_within_onek})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 무드키워드 음성 문장
class Moodkeywords_sentence(BaseModel):
    userId: str
    sentence: str


@app.post("/keywords/mood/speech")
async def process_moodkeywords(moodkeywords_sentence: Moodkeywords_sentence):
    processed_result = moodKeywords_sentence_to_our_keywords(moodkeywords_sentence.sentence)

    return JSONResponse(content={"userId": moodkeywords_sentence.userId,
                                "words": processed_result})


async def request_onek_rest_list_to_redis(roomId):
    url = "http://43.203.17.229:8080/api/restaurants/simple"
    room_id = roomId

    headers = {'Content-Type': 'application/json'}
    params = {"roomId": room_id}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        result_data = response.json()
        return result_data
    else:
        print("request to redis server has failed!!", response.status_code)

# 확정된 무드키워드로 추천 식당 요청
class Recommand_for_one(BaseModel):
    userId: str
    roomId: str
    newMoods: list
    categories: list


@app.post("/restaurants/forone")
async def recommand_for_one(recommand_for_one: Recommand_for_one):
    redis_result = await request_onek_rest_list_to_redis(recommand_for_one.roomId)
    # print("redis_result::::::", redis_result)
    processed_result = restaurants_for_one(recommand_for_one, redis_result)

    return JSONResponse(content={"userId": recommand_for_one.userId,
                                "restaurant_id_list": processed_result})


class Foodcategories_senctence(BaseModel):
    userId: str
    sentence: str


@app.post("/foodcategories/speech")
async def process_foodcategories(foodcategories_senctence: Foodcategories_senctence):
    processed_result = tockenizing_foodcategory(foodcategories_senctence.sentence)

    return JSONResponse(content={"userId": foodcategories_senctence.userId,
                                 "words": processed_result})


# 교집합 추천 식당 요청
class Recommand_for_many(BaseModel):
    roomId: str
    restaurant_id_list: list
    user_coords: list


@app.post("/restaurants/formany")
async def recommand_for_many(recommand_for_many: Recommand_for_many):
    num_users = 4
    center_res = []
    processed_result = []
    user_id_list = recommand_for_many.restaurant_id_list
    redis_result = await request_onek_rest_list_to_redis(recommand_for_many.roomId)
    await get_rest_within_onek_from_redis(redis_result)


    # 프론트에서 받은 식당 네개 먼저 processed_result에 추가하기
    for id in user_id_list:
        processed_result.append(id)

    # 센터 계산하기
    processed_result_1 = []
    processed_result_2 = []
    processed_result_1 = restaurants_for_many(user_id_list[:2], recommand_for_many) # a & b
    print('processed_result_1', processed_result_1)
    processed_result_2 = restaurants_for_many(user_id_list[2:4], recommand_for_many) # c & d
    print('processed_result_2: ', processed_result_2)

    comb_abcd = [processed_result_1[0]]
    comb_abcd.append(processed_result_2[0])
    print('comb_abcd: ', comb_abcd)

    center_res = restaurants_for_many(comb_abcd, recommand_for_many) # cent
    print('center_res: ', center_res)
    print('center_res type: ', type(center_res))

    # 센터와 각 4개 식당 계산하기
    user_a = [user_id_list[0]]
    user_b = [user_id_list[1]]
    user_c = [user_id_list[2]]
    user_d = [user_id_list[3]]
    print("user_a = [user_id_list[0]]: ", user_a)

    user_a.append(center_res[0])
    print("user_a.append(center_res): ", user_a)
    user_b.append(center_res[0])
    user_c.append(center_res[0])
    user_d.append(center_res[0])

    each_with_center = []
    user_a_results = restaurants_for_many(user_a, recommand_for_many)
    each_with_center.append(user_a_results[5])
    print('each_with_center after user a: ', each_with_center)
    user_b_results = restaurants_for_many(user_b, recommand_for_many)
    each_with_center.append(user_b_results[5])
    print('each_with_center after user b: ', each_with_center)
    user_c_results = restaurants_for_many(user_c, recommand_for_many)
    each_with_center.append(user_c_results[5])
    print('each_with_center after user c: ', each_with_center)
    user_d_results = restaurants_for_many(user_d, recommand_for_many)
    each_with_center.append(user_d_results[5])
    print('each_with_center after user d: ', each_with_center)

    for i in range(4):
        processed_result.append(each_with_center[i])

    processed_result.append(center_res[0])
    print('processed_result: ', processed_result)

    return JSONResponse(content={"restaurant_id_list": processed_result})