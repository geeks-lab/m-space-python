import numpy as np
import pandas as pd
import ast

# CSV 파일 읽기
df = pd.read_csv('/Users/finallyfinn/Desktop/projects/krafton/backend-python/app/assets/updated_swapped_coordinates.csv')

# 'vector' 컬럼을 NumPy 배열로 변환하여 벡터 데이터 집합 만들기
vector_dataset = [np.array(ast.literal_eval(vector_str)) if pd.notna(vector_str) else None for vector_str in
                  df['vector']]

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


def restaurants_for_two(rest_id_list):
    rest_a_vec = restid_to_restvec(rest_id_list[0])
    rest_b_vec = restid_to_restvec(rest_id_list[1])



    mid_res_list = []

    # 일치하는 '_id' 찾아서 리스트에 저장
    matching_ids = find_matching_ids(mid_res_list)



    # 결과 출력
    print("Matching '_id' 리스트:")
    print('matching_ids: ', matching_ids)

    return matching_ids


# list_temp = ['65ad3d685a419523bb3583a9', '65ad3d685a419523bb3583b2']
# restaurants_for_two(list_temp)




