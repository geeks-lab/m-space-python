import numpy as np
import pandas as pd
from bson import ObjectId
from geopy.geocoders import Nominatim
from haversine import haversine, Unit
import requests
from dotenv import load_dotenv
import os
import json

from pymongo import MongoClient

client = MongoClient('mongodb+srv://jiyoung:jiyoung1234^^@favsniper.gg9uyie.mongodb.net/?retryWrites=true&w=majority')
db = client['sniper']
collection = db['restaurant']


load_dotenv()

def to_float(value):
    try:
        float_value = float(value)
        if not np.isfinite(float_value):
            raise ValueError("Non-finite float value")
        return float_value
    except (ValueError, TypeError):
        return None

def convert_coords_to_address(latitude, longitude):
    url = f'https://dapi.kakao.com/v2/local/geo/coord2address.json'
    db_host = os.getenv("KAKAO_API_KEY")
    params = {
        'x': latitude,
        'y': longitude,
    }

    headers = {'Authorization': f'KakaoAK {db_host}'}
    response = requests.get(url, params=params, headers=headers)
    try:
        address = response.json()['documents'][0]['address']['address_name']
        return address
    except (KeyError, IndexError):
        print('KAKAO API request failed!')
        return None

# API
def api_restaurants_within_onek(restaurants_within_onek):
    user_id = restaurants_within_onek.userId
    base_coords = restaurants_within_onek.base_coords
    longitude = base_coords[0]
    latitude = base_coords[1]
    given_address = convert_coords_to_address(latitude, longitude)
    if given_address is None:
        print("주소를 찾을 수 없습니다.")
        return []

    current_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_path, "../assets/merged_data.csv")
    csv_path = os.path.normpath(csv_path)

    df = pd.read_csv(csv_path)
    df['address'] = df['address'].fillna('')
    second_word = given_address.split()[1]  # '강남구'
    filtered_data = df[df['address'].apply(lambda x: len(x.split()) > 1 and x.split()[1] == second_word)]
    gu_rest_dict_list = filtered_data.to_dict(orient='records')

    nearby_restaurants = []
    for result_dict in gu_rest_dict_list:
        coord_str = result_dict.get('coordinates')  # 두번째 옵션은 디폴트값 만약 첫번째 없을시에
        if coord_str and coord_str.lower() != 'none':
            coords = [to_float(coord) for coord in coord_str.replace("'", "").strip('[]').split(', ')]
            if None not in coords:
                distance = haversine(base_coords, (coords[0], coords[1]), unit=Unit.KILOMETERS)
                if distance <= 1.5:
                    nearby_restaurants.append(result_dict)
    # # CSV 파일로 저장
    # if nearby_restaurants:
    #     nearby_df = pd.DataFrame(nearby_restaurants)
    #     nearby_df.to_csv(f'/Users/finallyfinn/Desktop/projects/krafton/backend-python/app/assets/restaurants_within_onek_{user_id}.csv')
    #     print(f'csv for {user_id} has been downloaded!')

    rest_id_list = []
    for rest in nearby_restaurants:
        rest_id_list.append(rest["_id"])
    print('예외처리 전 restranst id list length: ', len(rest_id_list))

    # # undefined 예외처리
    # for compared_id in rest_id_list:
    #     object_id = ObjectId(compared_id)
    #     db_rest = collection.find_one({"_id": object_id})
    #     if db_rest:
    #         if object_id == db_rest["_id"]:
    #             rest_cursor = collection.find({'$or': [
    #                 {'food_category': {'$exists': False}},
    #                 {'foodCategories': {'$exists': False}},
    #                 {'moodKeywords': {'$exists': False}},
    #                 {'moodKeywords': []}
    #             ]})
    #             for rest in rest_cursor:
    #                 if rest['_id'] in rest_id_list:
    #                     rest_id_list.remove(rest['_id'])
    #                     print(f'restaurants id {rest["_id"]} has been deleted as either food_category, foodCategories'
    #                           f' or moodKeywords was undefined')
    #
    # print('예외처리 후 restranst id list length: ', len(rest_id_list))


    print(f' 1km 이내의 식당 수: {len(rest_id_list)}')
    num_res_within_onek = len(rest_id_list)
    return rest_id_list, num_res_within_onek

