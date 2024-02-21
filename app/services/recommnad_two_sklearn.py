import re
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
import os
import copy
from pymongo import MongoClient
import ast
from collections import OrderedDict
from sklearn.neighbors import NearestNeighbors
from geopy.distance import geodesic

load_dotenv()
client = MongoClient('mongodb+srv://jiyoung:jiyoung1234^^@favsniper.gg9uyie.mongodb.net/?retryWrites=true&w=majority')
db = client['sniper']
collection = db['restaurant']

current_path = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_path, "../assets/swapped_coordinates.csv")
csv_path = os.path.normpath(csv_path)

df = pd.read_csv(csv_path)

vector_dataset = []
vector_dataset_info_lis = []
restaurants_dict_from_redis_original = []
restaurants_dict_from_redis = []
nearby_restaurants_redis = []
user_coordinates = []


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
        else:
            print('could not find the matching id on restid_to_restvec()')

# a vec, b vec
# c = a + b / 2 => calculating just the average of each dimension..
# get the closest three indices from the c..hmm
def getting_mid_c_indices(rest_a_vec, rest_b_vec):
    print('rest_a_vec in getting_mid_c_indices(): ', rest_a_vec)
    print('rest_b_vec in getting_mid_c_indices(): ', rest_b_vec)


    vector_A = np.array(rest_a_vec)
    vector_B = np.array(rest_b_vec)

    print('vector_A: ', vector_A)
    print('vector_A type: ', type(vector_A))
    print('vector_B: ', vector_B)
    print('vector_B type: ', type(vector_B))

    if type(vector_A.all() or vector_B.all()) is None:
        return print('error: one of the vector is none')

    vector_C = (vector_A + vector_B) / 2

    # vector_dataset에 있는 모든 벡터와 vector_C 간의 거리를 유클리드 거리 계산
    distances = np.linalg.norm(vector_dataset - vector_C, axis=1)
    nearest_indices = np.argsort(distances)[:3]
    # distances 배열에서 최소값을 갖는 인덱스 찾기
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
    print('mood_keywords_list: ', mood_keywords_list)
    return mood_keywords_list


def parse_string_with_spaces(input_string):
    pattern = r'\d+'
    input_string = str(input_string)
    print('input_string: ', input_string)
    numbers = re.findall(pattern, input_string)
    print('numbers 111: ', numbers)
    numbers = [int(num) for num in numbers]
    print('numbers 222: ', numbers)
    return numbers

def restaurants_for_many(restaurant_id_list, recommand_for_many):
    #print('restaurants_for_many function has been called! asdfasdbe')
    #print('vector_dataset len', len(vector_dataset))
    global restaurants_dict_from_redis
    global restaurants_dict_from_redis_original

    restaurants_dict_from_redis = copy.copy(restaurants_dict_from_redis_original)
    #print('copytest11(original)', len(restaurants_dict_from_redis_original))
    #print('copytest11', len(restaurants_dict_from_redis)) # 129

    user_coordinates = recommand_for_many.user_coords
    #print('restaurant_id_list[0] : ', restaurant_id_list[0])
    #print('restaurant_id_list[1] : ', restaurant_id_list[1])
    two_vectors = []
    two_vectors.append(restid_to_restvec(restaurant_id_list[0])) # 얘가 rest['id']에 없어서 자꾸 None 찍힘
    two_vectors.append(restid_to_restvec(restaurant_id_list[1]))
    #print('two::::',two_vectors[0][0]) # 여기 같음.......하.......
    #print('two::::', two_vectors[1][0])

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
        print('rest_c_indices: ', rest_c_indices) #  [49 36 80]
        for index in rest_c_indices:
            distances, indices = knn_model.kneighbors([vector_dataset[index]])
            flat_indices = indices[0]  # [[21 84 16 14]] -> [21 84 16 14]
            print('flat_indices: ', flat_indices)
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
        print('1111 vec -> id is done')
        print('copytest22(original)', len(restaurants_dict_from_redis_original))
        print('copytest11', len(restaurants_dict_from_redis))

        '''
        result_res_ids_set : 중간지점에서 가까운 벡터 몇개 식당 아이디 리스트
        rest_ids_from_mood_keywords_list : 이 벡터들의 무드와 일치되는 식당리스트 (완전 일치 되는게 한 개 미만일시, 부분 일치로 가져옴)
                                        이 식당들은 유저 위치로부터 1키로 반경 내 아니라 서울 전체 구임
        '''
        #result_res_ids_unique = list(OrderedDict.fromkeys(result_res_ids_set))  # dict 중복제거
        mood_keywords_list = res_id_to_moodKeywords(result_res_ids_set)
        print('mood_keywords_list: ', mood_keywords_list)
        # 해당 분위기의 식당 리스트 꾸리기 from the csv
        rest_ids_from_mood_keywords_list = []
        if len(mood_keywords_list) > 1:
            # 무드키워드 [첫번째] 키워드랑 일치하는 레스토랑 리스트에 추가
            mk_list_a = df.loc[
                df['newMoods'].apply(lambda x: ast.literal_eval(x) == mood_keywords_list[0]), '_id'].tolist()
            rest_ids_from_mood_keywords_list += mk_list_a
            print('a rest_ids_from_mood_keywords_list: ', rest_ids_from_mood_keywords_list)
            print('rest_ids_from_mood_keywords_list len: ', len(rest_ids_from_mood_keywords_list))

            # 무드키워드 [첫번째,두번째] 키워드랑 순서까지 일치하는 레스토랑 리스트에 추가
            print('mood_keywords_list[:2]: ', mood_keywords_list[:2])
            mk_list_ab = df.loc[df['newMoods'].apply(
                lambda x: all(keyword in ast.literal_eval(x) for keyword in mood_keywords_list[:2])), '_id'].tolist()
            rest_ids_from_mood_keywords_list += mk_list_ab
            print('ab rest_ids_from_mood_keywords_list: ', rest_ids_from_mood_keywords_list)
            print('rest_ids_from_mood_keywords_list len: ', len(rest_ids_from_mood_keywords_list))

            # 무드키워드 [두번째,첫번째] 키워드랑 순서까지 일치하는 레스토랑 리스트에 추가
            ba = [mood_keywords_list[1]]
            ba.append(mood_keywords_list[0])
            print('ba: ', ba)
            mk_list_ba = df.loc[df['newMoods'].apply(
                lambda x: all(keyword in ast.literal_eval(x) for keyword in mood_keywords_list[:2])), '_id'].tolist()
            rest_ids_from_mood_keywords_list += mk_list_ba
            print('ba rest_ids_from_mood_keywords_list: ', rest_ids_from_mood_keywords_list)
            print('rest_ids_from_mood_keywords_list len: ', len(rest_ids_from_mood_keywords_list))

            # 무드키워드 [첫번째 or 두번째] 키워드랑 일치하는 레스토랑 리스트에 추가
            blist = mood_keywords_list[1]
            mk_list_b = df.loc[df['newMoods'].apply(lambda x: blist in ast.literal_eval(x)[0]), '_id'].tolist()
            rest_ids_from_mood_keywords_list += mk_list_b
            print('b rest_ids_from_mood_keywords_list: ', rest_ids_from_mood_keywords_list)
            print('rest_ids_from_mood_keywords_list len: ', len(rest_ids_from_mood_keywords_list)) # 500개정도..


        print('rest_ids_from_mood_keywords_list len: ', len(rest_ids_from_mood_keywords_list))
        matching_restaurant_ids = []
        # 무드키워드 일치하는 서울시의 모든 레스토랑에서 반경 1키로 내에 해당하는 식당들만 남기기
        for restid_from_broad_list in rest_ids_from_mood_keywords_list:
            for rest in restaurants_dict_from_redis:
                if rest['id'] == restid_from_broad_list:
                    matching_restaurant_ids.append((restid_from_broad_list))
                    break

        mooded_rest_within_onek = matching_restaurant_ids
        print('mooded_rest_within_onek len: ', len(mooded_rest_within_onek))  # 2
        print('2222 moodKeywords -> rest_ids(rest_ids_from_mood_keywords_list) is done')


        # 해당 무드 키워드와 일치하는 서울 모든 식당의 좌표값을 vector_dataset_info_list 안f에 딕셔너리에 업데이트하기
        for rest_id in mooded_rest_within_onek:
            try:
                rest_data = df[df['_id'] == rest_id]
            except:
                print(f"{rest_id}'s rest_data = df[df['_id'] == rest_id] failed!")
            if not rest_data.empty:
                coordinates_str = rest_data['coordinates'].values[0]  # CSV에서 좌표값 가져오기
                coordinates = ast.literal_eval(coordinates_str) if pd.notna(coordinates_str) else None
                if coordinates:
                    for item in restaurants_dict_from_redis:
                        if item['id'] == rest_id:
                            item['coordinates'] = coordinates
                            break

        # 식당 리스트에서 유저 위치로부터 가까운 순으로
        user_coordinates_tuple = tuple(user_coordinates)

        #te_restaurants_dict_from_redi = copy.copy(restaurants_dict_from_redis)

        temp_num = 0
        # 각 데이터포인트와 사용자 위치 사이의 거리 계산후 vector_dataset_info_list 안에 딕셔너리에 추가하기
        for item in restaurants_dict_from_redis:
            if 'coordinates' in item:
                rest_coordinates = tuple(item['coordinates'])
                distance = geodesic(user_coordinates_tuple, rest_coordinates).kilometers
                item['distance'] = distance
            else:
                restaurants_dict_from_redis.remove(item)
                temp_num += 1
                print(f"{item['id']} has been deleted on the te_restaurants_dict_from_redis list")
        print(f'total {temp_num} item has been deleted from the te_restaurants_dict_from_redis list ')


        # 거리 가까운 순으로 정렬
        sorted_vector_dataset_info_list = sorted(restaurants_dict_from_redis, key=lambda x: x['distance']
                                                    if 'distance' in x else float('inf'))

        # 가장 가까운 9개의 식당벡터데이터를 _id를 추출하여 리스트에 추가
        closest_nine_rests_ids = [it['id'] for it in sorted_vector_dataset_info_list[:9]]

        print('closest_nine_rests_ids: ', closest_nine_rests_ids)
        return closest_nine_rests_ids

    else:
        print('len(two_vectors) == 2 가 아니라는 뜻')
        return None
