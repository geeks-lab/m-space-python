
'''
// http://localhost:8000/api/matching-mkeywords

{
  "message": "success",
  "result": "Logic performed"
}
'''
import os

import pandas as pd
from gensim.utils import simple_preprocess
from konlpy.tag import Okt
from gensim.models import Word2Vec

'''
리뷰 데이터로 학습시켜서 모델 저장하기
'''
# csv_file_path = '../assets/restaurant_data2.csv'
# df = pd.read_csv(csv_file_path)
#
# # 'reviews' 컬럼에서 문장을 추출
# sentences = df['reviews'].astype(str).tolist()
#
# # 토큰화된 문장 리스트 생성
# tokenized_sentences = [simple_preprocess(sentence) for sentence in sentences]
#
# # Word2Vec 모델 학습
# model = Word2Vec(sentences=tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4)
#
# # 학습된 모델 저장
# model.save('../assets/mymodelfromreviews/modelfromreviews2.model')



def extract_adjectives(text):
    okt = Okt()
    pos_result = okt.pos(text)
    words = []
    for word, pos in pos_result:
        if pos in 'Adjective':
            words.append(word)
    return words

current_path = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_path, "../assets/mymodelfromreviews/updated_model.model")
model_path = os.path.normpath(model_path)

model = Word2Vec.load(model_path)

def compute_similarity(model, word1, word2):
    try:
        similarity = model.wv.similarity(word1, word2)
        return similarity
    except KeyError as e:
        print(f"Error: {e}")
        return None

def calculate_similarity_for_combinations(model, list1, list2):
    similarities = []

    for word1 in list1:
        for word2 in list2:
            similarity = compute_similarity(model, word1, word2)
            if similarity is not None:
                similarities.append((word1, word2, similarity))
    return similarities

moodKeywords = ['평화로운', '러블리한', '소박한', '앤틱한', '친절한', '모던한', '힐링', '서정적인', '로맨틱한', '조용한', '고즈넉한', '오붓한', '쾌적한', '활기찬', '우아한', '포근한', '신선한', '아늑한', '캐주얼한', '빈티지한', '예쁜', '복고풍', '럭셔리한', '근사한', '조그마한', '심플한', '고풍스러운', '트렌디한', '화려한', '세련된', '편안한', '느낌있는', '넓은', '힙한', '아기자기', '안락한', '시끌벅적한', '서민적인', '평온한', '유니크한', '화사한', '깨끗한', '전통적인', '낭만적인', '깔끔한', '고급스러운', '이국적', '아담한']


def moodKeywords_sentence_to_our_keywords(text):
    extracted_adjectives = extract_adjectives(text)
    similarities = calculate_similarity_for_combinations(model, extracted_adjectives, moodKeywords)

    top_similarities_dict = {}
    for word1 in extracted_adjectives:
        similar_words = sorted(moodKeywords, key=lambda x: compute_similarity(model, word1, x), reverse=True)[:3]
        top_similarities_dict[word1] = similar_words

    print("\nTop 5 similarities:")
    for word1, similar_words in top_similarities_dict.items():
        print(f"Top similarities for '{word1}': {similar_words}")

    top_5moods_dict = [{'word1': word1, 'top_5_moods': sorted(similar_words, key=lambda x: compute_similarity(model, word1, x), reverse=True)[:3]} for word1, similar_words in top_similarities_dict.items()]

    print("\ntop_5moods_dict:", top_5moods_dict)
    return top_5moods_dict






