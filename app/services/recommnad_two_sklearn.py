import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
import os
from pymongo import MongoClient
import ast
from collections import OrderedDict
from sklearn.neighbors import NearestNeighbors
from geopy.distance import geodesic

load_dotenv()
client = MongoClient('mongodb+srv://jiyoung:jiyoung1234^^@favsniper.gg9uyie.mongodb.net/?retryWrites=true&w=majority')
db = client['sniper']
collection = db['user_csv']

current_path = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_path, "../assets/swapped_coordinates.csv")
csv_path = os.path.normpath(csv_path)

df = pd.read_csv(csv_path)

# Load vector dataset from MongoDB
vector_dataset = []
vector_dataset_info_list = []
for item in collection.find({}):
    if 'vector' in item:
        vector_str = item['vector']
        if pd.isna(vector_str):  # NaN 값 처리
            continue
        else:
            vector = ast.literal_eval(vector_str)
            vector_info = {
                '_id': item['_id'],
                'name': item['name'],
                'moodKeywords': item['moodKeywords'],
                'vector': vector,
                'coordinates': []
            }
            vector_dataset_info_list.append(vector_info)
            vector_dataset.append(vector)

vector_dataset = np.array(vector_dataset)


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


# def find_matching_ids(target_vectors):
#     matching_ids = []
#     for target_vector in target_vectors:
#         for item in collection.find({"vector": {"$exists": True}}):
#             current_vector = ast.literal_eval(item['vector'])
#             if not np.isnan(current_vector).any() and not np.isnan(target_vector).any():
#                 if np.array_equal(target_vector, current_vector):
#                     matching_ids.append(item['_id'])
#     return matching_ids

def find_matching_ids(target_vectors):
    df = pd.read_csv(csv_path)

    # Add commas between float values in target_vectors
    formatted_vectors = []
    for tvector in target_vectors:
        formatted_vector = "[" + ", ".join(map(str, vector)) + "]"
        formatted_vectors.append(formatted_vector)

    matching_ids = df.loc[df['vector'].isin(formatted_vectors), '_id'].tolist()

    # Check if any target vector does not have a matching value in the DataFrame
    for target_vector, formatted_vector in zip(target_vectors, formatted_vectors):
        if not df['vector'].isin([formatted_vector]).any():
            print("No matching vector found for:", formatted_vector)

    return matching_ids

    # if not isinstance(target_vectors, list):
    #     target_vectors = [target_vectors]  # 단일 벡터일 경우 리스트로 변환
    #     print('list로 변환함요')
    #
    # matching_ids = df.loc[df['vector'].isin(target_vectors), '_id'].tolist()
    #
    # for target_vector in target_vectors:
    #     print('target_vector 후 : ', target_vector)
    #     if not df['vector'].isin([target_vector]).any():
    #         print("No matching vector found for:", target_vector)
    #
    # return matching_ids

    # for target_vector in target_vectors: # nearest 다섯개
    #     print('targ vec: ', target_vector)
    #     print('target_vector with str', str(target_vector))
    #     target_vector_str = str(target_vector)
    #     print('str(target_vector) type', type(str(target_vector)))
    #     target_vector_str_with_quotes = '"' + target_vector_str + '"'
    #     print('target_vector_str_with_quotes: ', target_vector_str_with_quotes)
    #
    #     # if np.isnan(target_vector).any():
    #     #     print('벡터 리스트에 nan 있음')
    #     dbdata = db.collection.find({"vector": target_vector_str_with_quotes})
    #     for itm in dbdata:
    #         print("itm['_id']: ", str(itm['_id']))
    #         matching_ids.append(str(itm['_id']))
    #         return matching_ids

    # db_data_list_from_db = list(db_data)ß
    # print('db_data_list_from_db :', db_data_list_from_db)
    # for it in db_data_list_from_db:
    #     print('it:', it)
    #     #print("item['_id']: ", it['_id'])
    #     matching_ids.append(it['_id'])
    #     print('appended!')
    # return matching_ids


#             print("item['vector']", item['vector'])
#             print("item['vector'] type: ", type(item['vector'])) # item['vector'] type:  <class 'str'>
#             vec_value_from_db = ast.literal_eval(item['vector'])
#             print('vec_value_from_db: ', vec_value_from_db)
#             print('vec_value_from_db type: ', type(vec_value_from_db)) # current_vector type:  <class 'list'>
#
#             if not np.isnan(vec_value_from_db).any() and not np.isnan(target_vector).any(): # 여기 item['vector']
#                 if np.array_equal(target_vector, vec_value_from_db):
#                     matching_ids.append(item['_id'])
#             test_num += 1
#             print('test_num: ', test_num)
#     return matching_ids
#
# def find_matching_ids(target_vectors):
#     matching_ids = []
#     for target_vector in target_vectors:
#         cursor = collection.find({"vector": target_vector})
#         for item in cursor:
#             matching_ids.append(item['_id'])
#     return matching_ids

def restid_to_restvec(rest_id):
    result = collection.find_one({"_id": rest_id})
    if result and 'vector' in result:
        vector_str = result['vector']
        desired_vector = ast.literal_eval(vector_str) if pd.notna(vector_str) else None
        print(f"The 'vector' value for the desired id '{rest_id}' is: {desired_vector}")
        return desired_vector
    else:
        print(f"No matching document found for the desired id '{rest_id}'.")
        return None


def getting_mid_c_indices(rest_a_vec, rest_b_vec):
    vector_A = np.array(rest_a_vec)
    vector_B = np.array(rest_b_vec)
    vector_C = (vector_A + vector_B) / 2

    # vector_dataset에 있는 모든 벡터와 vector_C 간의 거리를 유클리드 거리 계산
    distances = np.linalg.norm(vector_dataset - vector_C, axis=1)
    nearest_indices = np.argsort(distances)[:3]
    # distances 배열에서 최소값을 갖는 인덱스 찾기
    return nearest_indices


def res_id_to_moodKeywords(result_res_ids_set):
    result_moodkeywords = []
    for res_id in result_res_ids_set:
        for _ in range(3):
            result_data_from_db = collection.find_one({"_id": res_id})
            if result_data_from_db and 'moodKeywords' in result_data_from_db:
                mood_keywords_str = result_data_from_db['moodKeywords']
                mood_keywords_list = eval(mood_keywords_str)
                result_moodkeywords.append(mood_keywords_list[0])
    print('result_moodkeywords: ', list(set(result_moodkeywords))[:2])
    return list(set(result_moodkeywords))[:2]


def restaurants_for_many(restaurant_id_list):
    print('restaurants_for_many function has been called!')
    vectors = []
    for rest_id in restaurant_id_list:
        result = collection.find_one({"_id": rest_id})
        if result and 'vector' in result:
            vector = ast.literal_eval(result['vector'])
            vectors.append(vector)

    k = 5
    knn_model = NearestNeighbors(n_neighbors=k)
    knn_model.fit(vector_dataset)

    result_res_ids = []

    if len(vectors) >= 2:
        rest_c_indices = getting_mid_c_indices(vectors[0], vectors[1])
        idx_for_indices_list = 0
        nearest_indices = []
        nearest_vectors = []
        for index in rest_c_indices:
            distances, indices = knn_model.kneighbors([vector_dataset[index]])  # 여기
            flat_indices = indices[0]  # [[21 84 16 14]] -> [21 84 16 14]
            print('flat_indices: ', flat_indices)
            flat_indices_wt_comma = eval(str(flat_indices).replace("  ", " ").replace(" ", ", "))
            print('flat_indices_wt_comma: ', flat_indices_wt_comma)
            nearest_indices.append(flat_indices_wt_comma[idx_for_indices_list])
            idx_for_indices_list += 1
            # unique_nearest_indices = list(set(nearest_indices)) # 이거 중복제거하려고 넣었던 코드인데  [419, 525, 31, 506, 427] ->  [84, 21, 31] 이렇게 되서이상해서 뺌
            # print('unique_nearest_indices: ', unique_nearest_indices) #  [84, 21]
            # nearest_vectors = [vector_dataset[i] for i in unique_nearest_indices]

            for i in nearest_indices:
                nearest_vectors.append(vector_dataset[i])

            for vec in nearest_vectors:
                for itm in vector_dataset_info_list:
                    if np.array_equal(vec, itm['vector']):
                        result_res_ids.append(itm['_id'])
            result_res_ids_set = list(set(result_res_ids))  # 중복제거

        '''
        result_res_ids_set : 중간지점에서 가까운 벡터 몇개 식당 아이디 리스트
        rest_ids_from_mood_keywords_list : 이 벡터들의 무드와 일치되는 식당리스트 (완전 일치 되는게 한 개 미만일시, 부분 일치로 가져옴)
                                        이 식당들은 유저 위치로부터 1키로 반경 내 아니라 서울 전체 구임
        '''
        print('result_res_ids_set: ', result_res_ids_set)
        result_res_ids_unique = list(OrderedDict.fromkeys(result_res_ids_set))  # 중복제거
        print('result_res_ids_unique: ', result_res_ids_unique)
        mood_keywords_list = res_id_to_moodKeywords(result_res_ids_set)
        print('mood_keywords_list type: ', type(mood_keywords_list))
        # 해당 분위기의 식당 리스트 꾸리기 from the csv
        rest_ids_from_mood_keywords_list = df.loc[
            df['moodKeywords'].apply(lambda x: ast.literal_eval(x) == mood_keywords_list), '_id'].tolist()
        if 1 > len(rest_ids_from_mood_keywords_list):
            rest_ids_from_mood_keywords_list = df.loc[df['moodKeywords'].apply(
                lambda x: mood_keywords_list[0] in ast.literal_eval(x) or mood_keywords_list[1] in ast.literal_eval(
                    x)), '_id'].tolist()
        print('rest_ids_from_mood_keywords_list: ', rest_ids_from_mood_keywords_list)

        # 해당 무드 키워드와 일치하는 서울 모든 식당의 좌표값을 vector_dataset_info_list 안에 딕셔너리에 업데이트하기
        for rest_id in rest_ids_from_mood_keywords_list:
            rest_data = df[df['_id'] == rest_id]
            if not rest_data.empty:
                coordinates_str = rest_data['coordinates'].values[0]  # CSV에서 좌표값 가져오기
                print('coordinates_str: ', coordinates_str)
                coordinates = ast.literal_eval(coordinates_str) if pd.notna(coordinates_str) else None
                if coordinates:
                    for item in vector_dataset_info_list:
                        if item['_id'] == rest_id:
                            item['coordinates'] = coordinates
                            break

        # 식당 리스트에서 유저 위치로부터 가까운 순으로 3개 뽑기
        user_coordinates = [37.5001716373021, 127.029070884291] # TODO: 여기 서연이가 하면 넣기
        user_coordinates_tuple = tuple(user_coordinates)

        # 각 데이터포인트와 사용자 위치 사이의 거리 계산
        for item in vector_dataset_info_list:
            rest_coordinates = tuple(item['coordinates'])
            distance = geodesic(user_coordinates_tuple, rest_coordinates).kilometers
            item['distance'] = distance

        # 거리에 따라 데이터포인트를 정렬
        sorted_vector_dataset_info_list = sorted(vector_dataset_info_list, key=lambda x: x['distance'])

        # 가장 가까운 세 개의 데이터포인트의 _id를 추출하여 리스트에 추가
        closest_three_rests_ids = [it['_id'] for it in sorted_vector_dataset_info_list]

        print('closest_three_rests_ids: ', closest_three_rests_ids[:3])
        return closest_three_rests_ids[:3]

    else:
        print('레스토랑에 무드키워드가 없어서 아마 벡터값이 없어서 여기로 오게된 것일 겁니다.')
        return None
