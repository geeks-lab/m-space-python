import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from haversine import haversine, Unit
import requests
from dotenv import load_dotenv
import os
import json
from pymongo import MongoClient
import ast

from sklearn.neighbors import NearestNeighbors

load_dotenv()
# Connect to MongoDB
client = MongoClient('mongodb+srv://jiyoung:jiyoung1234^^@favsniper.gg9uyie.mongodb.net/?retryWrites=true&w=majority')
db = client['sniper']
collection = db['user_csv']

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

def find_matching_ids(target_vectors):
    matching_ids = []
    for target_vector in target_vectors:
        for item in collection.find({}):
            if 'vector' in item:
                current_vector = ast.literal_eval(item['vector'])
                if target_vector == current_vector:
                    matching_ids.append(item['_id'])
    return matching_ids

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

def getting_mid_c(rest_a_vec, rest_b_vec):
    vector_A = np.array(rest_a_vec)
    vector_B = np.array(rest_b_vec)
    vector_C = (vector_A + vector_B) / 2

    distances = np.linalg.norm(vector_dataset - vector_C, axis=1)
    nearest_index = np.argmin(distances)
    return nearest_index

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

    rest_c_vec = getting_mid_c(vectors[0], vectors[1])

    distances, indices = knn_model.kneighbors([vector_dataset[rest_c_vec]])
    nearest_vectors = [vector_dataset[i] for i in indices[0]]

    matching_ids = find_matching_ids(nearest_vectors)

    print("matching_ids '_id' 리스트:")
    print('matching_ids: ', matching_ids)

    return matching_ids

import ast

# Load vector dataset from MongoDB
vector_dataset = []
for item in collection.find({}):
    if 'vector' in item:
        vector_str = item['vector']
        if vector_str == 'NaN':  # NaN 값 처리
            vector = np.nan
        else:
            vector = ast.literal_eval(vector_str)
        vector_dataset.append(vector)

vector_dataset = np.array(vector_dataset)


