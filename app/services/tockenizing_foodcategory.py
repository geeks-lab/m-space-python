from konlpy.tag import Okt

def tockenizing_foodcategory(text):
    print(text)
    okt = Okt()
    pos_result = okt.pos(text)
    words = [word for word, pos in pos_result if pos in 'Noun' and len(word) > 1]
    words = [word for word in words if word not in ['오늘', '뭔가', '조금', '음식', '글쎄', '그러게']]
    print(words)
    return words

#text = "저는 오늘 한식이나 일식 아니면 양식도 괜찮고 베트남음식도 좋아요"

# words = tockenizing_foodcategory(text)
# print(words)


