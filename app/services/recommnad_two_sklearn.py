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

#TODO: 레디스에서 받은 레스토랑 아이디 -> 레스토랑 정보 가지는 전역 리스트 restaurants_dict_from_redis 만드는 함수
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
        # print('given rest_id: ', rest_id)
        # print('restaurants_dict_from_redis: rest: ', rest['id'])
        if rest_id == rest['id']:
            print('id has been matched on restid_to_restvec()')
            if len(rest['vector']) > 0:
                return rest['vector']
        # else:
            # print('matching has been failed!')

# a vec, b vec
# c = a + b / 2 => calculating just the average of each dimension..
# get the closest three indices from the c..hmm
def getting_mid_c_indices(rest_a_vec, rest_b_vec):
    # print('rest_a_vec in getting_mid_c_indices(): ', rest_a_vec)
    # print('rest_b_vec in getting_mid_c_indices(): ', rest_b_vec)


    vector_A = np.array(rest_a_vec)
    vector_B = np.array(rest_b_vec)
    #
    # print('vector_A: ', vector_A)
    # print('vector_A type: ', type(vector_A))
    # print('vector_B: ', vector_B)
    # print('vector_B type: ', type(vector_B))

    if type(vector_A.all() or vector_B.all()) is None:
        return print('error: one of the vector is none')

    vector_C = (vector_A + vector_B) / 2

    distances = np.linalg.norm(vector_dataset - vector_C, axis=1)
    nearest_indices = np.argsort(distances)[:3]
    return nearest_indices


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
    # print('mood_keywords_list: ', mood_keywords_list)
    return mood_keywords_list

def parse_string_with_spaces(input_string):
    pattern = r'\d+'
    input_string = str(input_string)
    # print('input_string: ', input_string)
    numbers = re.findall(pattern, input_string)
    # print('numbers 111: ', numbers)
    numbers = [int(num) for num in numbers]
    # print('numbers 222: ', numbers)
    return numbers

def restaurants_for_many(restaurant_id_list):
    global restaurants_dict_from_redis
    global restaurants_dict_from_redis_original

    restaurants_dict_from_redis = copy.copy(restaurants_dict_from_redis_original)
    two_vectors = []
    # print('restaurant_id_list[0]: ', restaurant_id_list[0])
    # print('restaurant_id_list[1]: ', restaurant_id_list[1])
    two_vectors.append(restid_to_restvec(restaurant_id_list[0]))
    two_vectors.append(restid_to_restvec(restaurant_id_list[1]))

    k = 5
    knn_model = NearestNeighbors(n_neighbors=k)
    if not vector_dataset:
        return print('vector dataset not exits')
    knn_model.fit(vector_dataset)

    result_res_ids = []
    # print('two_vectors: bcvgsf', two_vectors)
    # print(f'two_vectors[0]: {two_vectors[0]} ///// two_vectors[1]: {two_vectors[1]}')
    if len(two_vectors) == 2:
        rest_c_indices = getting_mid_c_indices(two_vectors[0], two_vectors[1])
        idx_for_indices_list = 0
        nearest_indices = []
        nearest_vectors = []
        result_res_ids_set = []
        # print('rest_c_indices: ', rest_c_indices)  # [49 36 80]
        for index in rest_c_indices:
            distances, indices = knn_model.kneighbors([vector_dataset[index]])
            flat_indices = indices[0]  # [[21 84 16 14]] -> [21 84 16 14]
            # print('flat_indices: ', flat_indices)
            re_indices = parse_string_with_spaces(flat_indices)

            nearest_indices.append(re_indices[idx_for_indices_list])
            idx_for_indices_list += 1

            for i in nearest_indices:
                nearest_vectors.append(vector_dataset[i])

            # vec -> id
            for vec in nearest_vectors:
                for itm in restaurants_dict_from_redis:
                    if np.array_equal(vec, itm['vector']):
                        result_res_ids.append(itm['id'])
            result_res_ids_set = list(set(result_res_ids))  # 중복제거
        # print('the length of result_res_ids_set: ', result_res_ids_set) # got the 3 ids
        # print('1111 vec -> id is done')
        # print('copytest22(original)', len(restaurants_dict_from_redis_original))
        # print('copytest11', len(restaurants_dict_from_redis))
        print('the result before the return: ', result_res_ids_set)
        return result_res_ids_set
    else:
        print('Input Restaurants id is less than two.')
        return None
