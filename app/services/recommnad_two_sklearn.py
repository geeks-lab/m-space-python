import numpy as np
import pandas as pd
import ast
from sklearn.neighbors import NearestNeighbors

# CSV 파일 읽기
# TODO: 여기서 csv는 0번 과정에서 를 지정 위치 1km 내로 정리된 리스트로 바꿔야함.
df = pd.read_csv('/Users/finallyfinn/Desktop/projects/krafton/backend-python/app/assets/updated_swapped_coordinates.csv')

# 'vector' 컬럼을 NumPy 배열로 변환하여 벡터 데이터 집합 만들기
unpadded_vector_dataset = [np.array(ast.literal_eval(vector_str)) for vector_str in df['vector'] if pd.notna(vector_str)] # None 값 제외

max_length = max(len(vector) for vector in unpadded_vector_dataset)

# 최대 길이를 기준으로 모든 벡터들을 패딩하기.
vector_dataset = [np.pad(vector, (0, max_length - len(vector)), mode='constant') for vector in unpadded_vector_dataset if vector is not None]

def find_matching_ids(target_vectors):
    # 일치하는 '_id' 찾아서 리스트에 저장
    matching_ids = []

    for target_vector in target_vectors:
        for index, row in df.iterrows():
            if pd.notna(row['vector']):
                current_vector = ast.literal_eval(row['vector'])
                if target_vector == current_vector:
                    matching_ids.append(row['_id'])

    return matching_ids

def restid_to_restvec(rest_id):

    # '_id' 컬럼이 원하는 단어와 일치하는 행 선택 후 'vector' 값 가져오기
    filtered_row = df[df['_id'].str.contains(rest_id, case=False, na=False)]
    if not filtered_row.empty:
        vector_str = filtered_row['vector'].iloc[0]
        desired_vector = ast.literal_eval(vector_str) if pd.notna(vector_str) else None
        print(f"The 'vector' value for the desired id '{rest_id}' is: {desired_vector}")
        return desired_vector
    else:
        print(f"No matching rows found for the desired id '{rest_id}'.")
        return None

def getting_mid_c(rest_a_vec, rest_b_vec):
    print('rest_a_vec: ', rest_a_vec)
    print('rest_b_vec: ', rest_b_vec)

    vector_A = np.array(rest_a_vec)
    vector_B = np.array(rest_b_vec)

    vector_C = (vector_A + vector_B) / 2

    # 벡터 C와 가장 가까운 벡터의 인덱스 찾기
    distances = np.linalg.norm(vector_dataset - vector_C, axis=1)  # 모든 벡터와 벡터 C 사이의 거리 계산
    nearest_index = np.argmin(distances)  # 거리가 가장 짧은 벡터의 인덱스 찾기

    return nearest_index

def restaurants_for_many(rest_id_list):
    print('restaurants_for_many function has been called!')
    vectors = []
    for rest_id in rest_id_list:
        # 해당 레스토랑이 데이터 프레임에 존재하는지 확인
        if any(df['_id'] == rest_id):
            # 데이터 프레임에서 벡터를 가져와 리스트에 추가
            vector = df.loc[df['_id'] == rest_id, 'vector'].values
            vectors.append(vector[0]) if len(vector) > 0 else None
    '''
    sklearn
    '''
    k = 5
    knn_model = NearestNeighbors(n_neighbors=k)
    knn_model.fit(vector_dataset)

    rest_c_vec = getting_mid_c(vectors[0], vectors[1])

    # finding the neighbors of vec_c
    distances, indices = knn_model.kneighbors([vector_dataset[rest_c_vec]])
    nearest_vectors = [vector_dataset[i] for i in indices[0]]

    '''
    결과
    '''
    # 일치하는 '_id' 찾아서 리스트에 저장
    matching_ids = find_matching_ids(nearest_vectors)

    # 결과 출력
    print("matching_ids '_id' 리스트:")
    print('matching_ids: ', matching_ids)

    return matching_ids
