import pandas as pd
from gensim.models import Word2Vec

# Word2Vec 모델 로드
model_path = '../app/assets/mymodelfromreviews/updated_model.model'
model = Word2Vec.load(model_path)

# CSV 파일 읽기
csv_file_path = 'address_added.csv'
df = pd.read_csv(csv_file_path)

# 'moodKeywords' 열의 요소를 벡터화하고 압축하여 'vector' 열에 추가
vectors = []

for mood_keywords in df['moodKeywords']:
    mood_vector = []

    for keyword in mood_keywords.split(','):
        # 대괄호, 세미콜론, 작은 따옴표 제거
        keyword = keyword.replace('[', '').replace(']', '').replace(';', '').replace("'", "").strip()

        # 모델의 vocabulary에 있는 단어에 대해서만 처리
        try:
            if keyword and keyword in model.wv:
                mood_vector.append(model.wv[keyword])
        except KeyError:
            print(f"Ignoring '{keyword}' as it is not present in the vocabulary.")

    # 모델 vocabulary에 있는 단어가 없으면 most_similar을 통해 대체값 사용
    if not mood_vector and mood_keywords:
        # 대괄호, 세미콜론 제거
        mood_keywords = mood_keywords.replace('[', '').replace(']', '').replace(';', '').strip()

        # 모델 vocabulary에 있는지 확인 후 처리
        if mood_keywords in model.wv:
            similar_words = model.wv.most_similar(positive=[mood_keywords], topn=5)
            for similar_word, _ in similar_words:
                similar_word = similar_word.strip()
                # 작은 따옴표 제거
                similar_word = similar_word.replace("'", "")
                try:
                    if similar_word and similar_word in model.wv:
                        mood_vector.append(model.wv[similar_word])
                except KeyError:
                    print(f"Ignoring '{similar_word}' as it is not present in the vocabulary.")

    # 여러 벡터를 압축하여 하나의 벡터로 만듭니다. (평균 사용)
    compressed_vector = sum(mood_vector) / len(mood_vector) if mood_vector else None
    # If compressed_vector is not None, convert it to a string with commas between values
    if compressed_vector is not None:
        vector_str = '[' + ', '.join(map(str, compressed_vector)) + ']'
    else:
        vector_str = None

    vectors.append(vector_str)

df['vector'] = vectors

# CSV 파일에 새로운 'vector' 열 저장
df.to_csv('18,000without_coordi.csv', index=False)
