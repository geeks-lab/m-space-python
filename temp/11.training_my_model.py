import gensim
import pandas as pd

df = pd.read_csv("restaurant_data2.csv")

review_text = df.reviews.apply(gensim.utils.simple_preprocess)

model = gensim.models.Word2Vec(
    window=7,
    min_count=1,
    workers=4
)

# 얼마나 자주 출력할지? 안중요할듯
model.build_vocab(review_text, progress_per=1000)

model.train(review_text, total_examples=model.corpus_count, epochs=model.epochs)

model.save("word2vec-from-reviews2.model")

model.wv.similarity(w1="조용한", w2="차분한")

model.wv.similarity(w1="활기찬", w2="오붓한")