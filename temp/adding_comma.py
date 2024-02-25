import pandas as pd

# CSV 파일 불러오기 (파일 경로는 적절히 수정해주세요)
csv_path = 'output_file.csv'
df = pd.read_csv(csv_path)

# 'vector' 컬럼의 각 요소에 쉼표 추가하여 새로운 열 생성
def format_vector(row):
    try:
        vector_list = eval(row['vector'])
        if all(isinstance(elem, (int, float)) for elem in vector_list):
            formatted_vector = '[' + ', '.join(map(str, vector_list)) + ']'
            return formatted_vector
        else:
            return 'Invalid vector format'
    except Exception as e:
        return 'Error: {}'.format(str(e))

df['vector_formatted'] = df.apply(format_vector, axis=1)

# 결과를 새로운 CSV 파일로 저장 (파일 경로는 적절히 수정해주세요)
output_csv_path = '../app/services/formatted_file.csv'
df.to_csv(output_csv_path, index=False)
