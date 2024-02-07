import pandas as pd

# CSV 파일 경로
csv_path = 'formatted_file.csv'

# CSV 파일 읽기
df = pd.read_csv(csv_path)
print(f"CSV 파일의 행 수: {len(df)}")
# 세 번째 컬럼 삭제
df = df.drop(df.columns[2], axis=1)

# 수정된 DataFrame을 CSV 파일로 저장
df.to_csv('updated_file.csv', index=False)