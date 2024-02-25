import re
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import os
import copy
from pymongo import MongoClient
import ast
from sklearn.neighbors import NearestNeighbors

load_dotenv()
client = MongoClient('mongodb+srv://jiyoung:jiyoung1234^^@favsniper.gg9uyie.mongodb.net/?retryWrites=true&w=majority')
db = client['sniper']
collection = db['restaurant']

current_path = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_path, "../assets/merged_data.csv")
csv_path = os.path.normpath(csv_path)

df = pd.read_csv(csv_path)

vector_dataset = []
restaurants_dict_from_redis_original = []
restaurants_dict_from_redis = []
nearby_restaurants_redis = []


def get_vector_from_csv(rest_id):
    restaurant_row = df[df['_id'] == rest_id]
    if restaurant_row.empty:
        print(f"No restaurant found with ID: {rest_id}")
        return None
    vector_str = restaurant_row['vector'].values[0]

    if pd.notna(vector_str):
        vector = ast.literal_eval(vector_str)
        return vector
    else:
        print(f"No vector found for restaurant with ID: {rest_id}")
        return None

# 레디스에서 받은 레스토랑 아이디 -> 레스토랑 정보 가지는 전역 리스트 restaurants_dict_from_redis 만드는 함수
async def get_rest_within_onek_from_redis(redis_result_from_main):
    print('get_rest_within_onek_from_redis() has been callled!')
    if not redis_result_from_main:
        return print('redis response error')
    nearby_restaurants_redis = redis_result_from_main.get("restaurantDtoList", [])
    print('num of res getting from the redis : ', len(nearby_restaurants_redis))

    for restaurant in nearby_restaurants_redis:
        vector = get_vector_from_csv(restaurant["id"])
        if vector is None:
            print(f'{restaurant["id"]}vector is not on the csv')
        else:
            #print(f'vector value on csv with rest ID: {restaurant["id"]}')
            restaurant_data = {
                "id": restaurant["id"],
                "food_category": restaurant["food_category"] if "food_category" in restaurant else None,
                "foodCategories": [restaurant["foodCategories"]] if "foodCategories" in restaurant else None,
                "newMoods": restaurant["newMoods"] if "newMoods" in restaurant else None,
                "menus": restaurant["menus"] if "menus" in restaurant else None,
                "vector": vector
            }
            restaurants_dict_from_redis_original.append(restaurant_data)
    print('num of res restaurants_dict_from_redis_original : ', len(restaurants_dict_from_redis_original))
    make_vector_dataset()


def make_vector_dataset():
    print('make_vector_dataset has been called')
    for rest in restaurants_dict_from_redis_original:
        redis_res_vector = rest.get('vector')
        if redis_res_vector is not None:
            vector_dataset.append(rest['vector'])
        else:
            print(f'vector on {rest["id"]} restaurants does not exit')
    print('vector dataset is set on the global variable: vector_dataset')


def restid_to_restvec(rest_id):
    print('len of the rest restaurants_dict_from_redis is what : ', len(restaurants_dict_from_redis))

    for rest in restaurants_dict_from_redis:
        if rest_id == rest['id']:
            print('id has been matched on restid_to_restvec()')
            if len(rest['vector']) > 0:
                return rest['vector']

# a vec, b vec
# c = a + b / 2 => calculating just the average of each dimension..
# get the closest three indices from the c..hmm
def getting_mid_c(rest_a_vec, rest_b_vec):
    vector_a = np.array(rest_a_vec)
    vector_b = np.array(rest_b_vec)
    if type(vector_a.all() or vector_b.all()) is None:
        return print('error: one of the vector is none')
    vector_c = (vector_a + vector_b) / 2
    return vector_c


def res_id_to_moodKeywords(result_res_ids_set):
    mood_keywords_list = []
    for res_id in result_res_ids_set:
        count = 0
        for rest_from_redis in restaurants_dict_from_redis:
            if res_id == rest_from_redis.get('id'):
                mood_list = rest_from_redis.get('newMoods', [])
                mood_keywords_list.extend(mood_list[:3])
                count += len(mood_list)
                if count >= 3:
                    break

    mood_keywords_list = list(set(mood_keywords_list))
    print('mood_keywords_list: ', mood_keywords_list)
    return mood_keywords_list

def parse_string_with_spaces(input_string):
    pattern = r'\d+'
    input_string = str(input_string)
    numbers = re.findall(pattern, input_string)
    numbers = [int(num) for num in numbers]
    return numbers

def restaurants_for_many(restaurant_id_list):
    global restaurants_dict_from_redis
    global restaurants_dict_from_redis_original
    idx_for_ooi = 0

    restaurants_dict_from_redis = copy.copy(restaurants_dict_from_redis_original)
    two_vectors = []
    two_vectors.append(restid_to_restvec(restaurant_id_list[0]))
    two_vectors.append(restid_to_restvec(restaurant_id_list[1]))

    k = 7
    knn_model = NearestNeighbors(n_neighbors=k)
    if not vector_dataset:
        return print('vector dataset not exits')
    knn_model.fit(vector_dataset)

    result_res_id = ""
    nearest_indices = []
    nearest_vectors = []
    result_res_ids = []
    result_res_ids_set = []
    if len(two_vectors) == 2:
        rest_c_vec = getting_mid_c(two_vectors[0], two_vectors[1])
        distances, indices = knn_model.kneighbors(rest_c_vec.reshape(1, -1)) # k = 5
        flat_indices = indices[0] # [[]] -> []
        parsed_indices_list = parse_string_with_spaces(flat_indices)
        for parsed_index in parsed_indices_list:
            nearest_indices.append(parsed_index)

        for i in nearest_indices:
            nearest_vectors.append(vector_dataset[i])

        # vec -> id
        for vec in nearest_vectors:
            for itm in restaurants_dict_from_redis:
                if np.array_equal(vec, itm['vector']):
                    result_res_ids.append(itm['id'])
        result_res_ids_set = list(set(result_res_ids))

        # out of index 방어코드
        s_index = len(result_res_ids_set) - 1
        idx_for_ooi = min(6, s_index) # center of the four rests 로부터 7th 번째로 먼 vector 선택
        print('idx_for_ooi: ', idx_for_ooi)

        return_rest_id = result_res_ids_set[idx_for_ooi]
        return return_rest_id
    else:
        print('Input Restaurants id is less than two.')
        return None