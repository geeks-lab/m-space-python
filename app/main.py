from starlette.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.services.finding_matching_mkeywords import moodKeywords_sentence_to_our_keywords
from app.services.tockenizing_foodcategory import tockenizing_foodcategory
from app.services.recommnad_one import restaurants_for_one
from app.services.recommnad_two_sklearn import restaurants_for_many
from app.services.restaurants_within_onek import api_restaurants_within_onek

app = FastAPI()

# 사용자 장소 반경 1km내 식당 리스트
class Restaurants_within_onek(BaseModel):
    userId: str
    base_coords: list

@app.post("/restaurants/withinonek")
async def restaurants_within_onek(restaurants_within_onek: Restaurants_within_onek):
    processed_result = api_restaurants_within_onek(restaurants_within_onek)
    return JSONResponse(content={"userId": restaurants_within_onek.userId,
                                "restaurant_id_list": processed_result})

# 무드키워드 음성 문장
class Moodkeywords_sentence(BaseModel):
    userId: str
    sentence: str

@app.post("/keywords/mood/speech")
async def process_moodkeywords(moodkeywords_sentence: Moodkeywords_sentence):
    processed_result = moodKeywords_sentence_to_our_keywords(moodkeywords_sentence.sentence)

    return JSONResponse(content={"userId": moodkeywords_sentence.userId,
                                "words": processed_result})

# 확정된 무드키워드로 추천 식당 요청
class Recommand_for_one(BaseModel):
    userId: str
    moodKeywords: list
    categories: list

@app.post("/restaurants/forone")
async def recommand_for_one(recommand_for_one: Recommand_for_one):
    processed_result = restaurants_for_one(recommand_for_one)

    return JSONResponse(content={"userId": recommand_for_one.userId,
                                "restaurants_id": processed_result})

# 교집합 추천 식당 요청
class Recommand_for_many(BaseModel):
    restaurant_id_list: list

@app.post("/restaurants/formany")
async def recommand_for_many(recommand_for_many: Recommand_for_many):
    processed_result = restaurants_for_many(recommand_for_many)

    return JSONResponse(content={"userId": recommand_for_one.userId,
                                "restaurants_id": processed_result})
