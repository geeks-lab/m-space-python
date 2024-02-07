import pickle
import pandas as pd
from ast import literal_eval

# CSV 파일 읽기
csv_path = 'output_file.csv'
df = pd.read_csv(csv_path)

# 'vector' 컬럼의 값을 파이썬 리스트로 변환하고, 컴마를 넣어줌
df['vector'] = df['vector'].apply(lambda x: literal_eval(x) if pd.notna(x) else [])

# Drop rows with empty lists in the 'vector' column
df = df[df['vector'].apply(lambda x: bool(x))]

# 'vector' 컬럼의 값을 리스트로 저장 (컴마 포함)
vectors_with_comma = df['vector'].apply(lambda x: '[' + ', '.join(map(str, x)) + ']').tolist()

# 새로운 CSV 파일로 저장
df['vector'] = vectors_with_comma
df.to_csv('updated_output_file.csv', index=False)
