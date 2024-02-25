import pandas as pd
import numpy as np

# CSV 파일 읽기
df = pd.read_csv('../app/assets/swapped_coordinates.csv')

# 'vector' 컬럼의 각 행을 리스트로 변환하여 'vector_list' 컬럼 추가
df['vector_list'] = df['vector'].apply(lambda x: [float(num) for num in x.replace("[", "").replace("]", "").split(",")] if isinstance(x, str) else np.nan)

# 업데이트된 DataFrame을 새로운 CSV 파일로 저장
df.to_csv('../app/assets/updated_swapped_coordinates.csv', index=False)

print("CSV 파일이 업데이트되었습니다.")