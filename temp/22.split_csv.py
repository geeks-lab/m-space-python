import pandas as pd

def split_rows_csv(input_csv, output_csv1, output_csv2):
    df = pd.read_csv(input_csv)

    # 행 개수를 반으로 나눕니다.
    half_rows = len(df) // 2

    # 첫 번째 CSV에는 처음부터 중간 행까지 저장합니다.
    df1 = df.iloc[:half_rows, :]
    df1.to_csv(output_csv1, index=False)

    # 두 번째 CSV에는 중간 행부터 끝까지 저장합니다.
    df2 = df.iloc[half_rows:, :]
    df2.to_csv(output_csv2, index=False)

# 사용 예시
input_csv_file = 'output2.csv'
output_csv_file1 = 'quarter3.csv'
output_csv_file2 = 'quarter4.csv'
split_rows_csv(input_csv_file, output_csv_file1, output_csv_file2)
