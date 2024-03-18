# backend-python

<a href="https://velog.io/@gigis-note/%EB%82%98%EB%A7%8C%EC%9D%98%EB%AC%B4%EA%B8%B0-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%ED%9A%8C%EA%B3%A05W">프로젝트 설명 & 내가 기여한 부분 from my blog</a>

## 팀이 어떤 것들을 했는지
우리 팀은 **맛스페이스** 라는 맛집 추천 웹서비스를 만들었다. 친구들 혹은 동료들끼리 함께 갈 식당을 정할 때 서로 원하는 취향과 먹고 싶은 음식을 맞추기 위해 시간을 많이 사용한다. 그래서 우리는 각자 취향의 교집합 혹은 중간 지점을 구해주면 어떨까 하는 발상에서 시작되었다.

기능을 한 줄로 요약하면 <U>개인의 취향에 맞는 식당을 추천</U>해주고, <U>식당과 식당의 중간 지점에 있는 식당들을 추천</U>해준다. 자세한건 아래 노션페이지에서 확인할 수 있다.

[github link]
(https://github.com/Moojuck-KJ3/backend-python)<br>
[팀 소개 노션 페이지](https://www.notion.so/aca822e2ff304d919aa8a945efa6f80c?pvs=4)

![](https://velog.velcdn.com/images/gigis-note/post/cfd9a1f1-5d6e-45d4-bd6c-331d969fb56c/image.png)



## 내가 어떤 것들을 했는지
**[main]**
* 추천 파이프라인 설계 및 알고리즘 구현 (python)
* 자체 언어 모델 구현
* 문장을 단어단위로 tockenize/연관단어 추출
* 데이터 수집/가공
* 추천 관련 백엔드 API 명세/개발 (FastAPI)

**[sub]**
* python 백엔드 Dockerizing
* 프로덕트 기획 단계에서 활발한 아이디어 제공 및 피드백
* UI/UX 아이디어 제공 및 피드백
* redis/mongodb를 통한 데이터 수집/가공

### 추천 파이프라인 설계 및 알고리즘 구현(python)
처음엔 단순하게 식당들이 가지고 있는 키워드 태그들을 가지고 각 식당을 벡터화 시켜서 식당 데이터셋을 꾸리고 A식당과 B식당 각각 특정 거리에 있는 이웃 식당들을 구하고 겹치는 교집합 이웃 식당들을 반환해주면 되겠다 라고 생각했는데, 실제로 해보니 겹치는게 존재하지 않는 경우가 많았다.

그래서 A벡터와 B벡터의 거리를 계산하고 그 중간 지점에서부터 이웃 식당들을 구하는 방식으로 변경했다. 거리를 계산하는데는 유클리드 알고리즘을 사용하였고 중간 지점에서부터 인접한 벡터들을 구할 때는 KNN알고리즘을 사용하였다. 

벡터 데이터셋에서 특정 벡터로부터 인접한 벡터들을 구할 때 코사인유사도를 사용하지 않고 KNN을 사용한 이유는 코사인 유사도 알고리즘이 데이터셋이 비교적 작고 차원이 높은 경우에 특히 유용하다고 알려져 있지만 코사인 유사도 알고리즘은 유사도 임계값을 설정하여 인접한 벡터를 결정하기 때문에 특정 백터 주변에 인접한 백터가 없는 경우에는 해당 알고리즘으로 인접한 백터를 구할 수 없기 때문에 아무리 멀어도 그나마 가까이 인접해 있는 백터를 알아낼 수 있는 KNN알고리즘을 사용하였다.

서비스는 총 4명의 사용자가 각자 선택한 식당을 넣으면 조합된 식당을 확인할 수 있는 기능이 있는데 이 때에도 알고리즘을 비슷하게 위의 방식과 비슷하게 짰다. A, B, C, D 의 식당이 있을 때 A와 B의 식당의 중간값과 C와 D식당의 중간값, 그리고 이들의 중간 값을 4명의 중간값, 센터값이라고 했을 때, 센터와 A의 중간값, 센터와 B의 중간값, 이런식으로 식당을 추천하였다.

그런데 아쉬운 점은 결국 내가 추천하는 식당은 백터 A와 B 사이의 중간 지점에 있는 백터 즉, A와 B로부터 가장 먼 백터였다. 그러니까, A와 B가 멀다면 이들의 중간 지점이 엉뚱하게 보일 수 있다는 것이다.
<img src="https://velog.velcdn.com/images/gigis-note/post/5af3c3ed-347b-41a0-aa28-76cf29f881ad/image.png" width="300" height="300">

그래서 완전 중간에 인접해 있는 백터들이 아니라 어느정도 떨어져 있는 백터들을 추천해 주었어야 했으면 더 합리적으로 보일 수 있었을 것 같다. (그랬더라면 시연때 최소한 4명의 중간 식당으로 디저트 가게가 나오는 참사는 막을 수 있었을 것 같기도...ㅠㅠ)

<img src="https://velog.velcdn.com/images/gigis-note/post/93f46317-abd2-471f-a881-97fb197f0b21/image.png
" width="300" height="300">

지금 코드 구현된 방식은 가장 가까이 인접한 벡터를 우선적으로 보여주는데 위와 같이 보여주고 싶으면 5번인덱스부터 7번인덱스 사이에 골라서 보여주는 방식으로 간단하게 바꿔볼 수도 있을 것 같다.

생각치도 못했는데 해보지 못해 아쉬운 점이 또 있는데 이미 잘 알려진 성능평가방법을 활용하여 알고리즘의 성능을 평가해보지 못한 것이다. 추후에 알고리즘을 개선한다면 순위 기반의 Precision, Recall, MAP, NDCG의 지표를 활용하여 알고리즘의 성능이 개선되는 정도를 확인하며 개발할 수 있을 것 같다.

### 자체 언어 모델 구현
단어를 백터라이징 하기 위해서는 언어모델이 필요한데 처음에 모르는 단어에 대한 대응이 word2vec 보다 뛰어나고 노이즈가 많은 코퍼스에서 강점을 가지는 fasttext를 선택하여 사용하였다. 그런데 실제로 돌려보니 유사성이 생각보다 좋지 않아서 사용하기 어려운 정도였다. 유사성은 숫자가 낮을 수록 유사한 것이라고 보는데, 유사하다고 생각하는 식당들이 덜 유사하다고 생각되는 식당들보다 유사성이 떨어지는 결과가 나온 것이다. 
(유사성은 유클리드거리의 거리로 판단했다.)

예를들어, 아래의 두 식당의 경우 사용한 분위기 태그가 비슷하니까 숫자가 낮을 것으로 예상한다.
>나폴리회관 강남역점,"['깔끔한', '시끌벅적한']
청담이상 강남역점,"['예쁜', '시끌벅적한']
**유클리드 거리: 1.205982344248324**

그런데 유사성이 떨어져보이는 아래의 두 식당이 위의 식당보다 숫자가 더 높아야하는데 오히려 더 낮게 나오는 현상을 확인할 수 있었다.

>나폴리회관 강남역점,"['깔끔한', '시끌벅적한']
대진도원참치 강남역점 ['조용한', '고급스러운']
**유클리드 거리: 0.6086120995497456**

그래서 이대로 이 모델을 사용할 수 없는 상황이었고, 다른 모델을 사용해볼까 하다가 수집해놓은 리뷰데이터들을 가지고 모델을 학습시키면 어떨까 하고 바로 실험해 보았는데 fasttext보다 기대한대로 유사성이 높게 잘 나오는 것을 확인할 수 있었다.

>나폴리회관 강남역점,"['깔끔한', '시끌벅적한']
청담이상 강남역점,"['예쁜', '시끌벅적한']
**유클리드 거리: 5.451761920716737**


>나폴리회관 강남역점,"['깔끔한', '시끌벅적한']
대진도원참치 강남역점 ['조용한', '고급스러운']
**유클리드 거리: 7.012567671092597**

### 문장을 단어단위로 tockenize/연관단어 추출
사용자가 원하는 음식점의 카테고리나, 식당의 분위기에 대한 정보를 입력받을 때 음성인식으로 받기로 해서 파이썬 서버에서 문장을 단어 단위로 토크나이즈하고 연관 단어를 추출하여 사용자에게 보여주는 것을 구현하였다. 토크나이즈는 코앤엘파이를, 연관 단어는 word2vec의 similarity 함수를 사용하여 우리가 정의한 키워드 중에 유사성이 높은 단어들을 보여주는 형식으로 구현하였다. 

### 데이터 수집/가공
오픈API로 가져올 수 있는 데이터는 한계가 있었고 공공데이터도 생각보다 우리가 필요로하는 데이터의 한계가 있었다. 그래서 어쩔 수 없이 불법적이지만 크롤링도 실력이지 않나..하는 합리화를 되새기면서 크롤링을 시작하였다.

나는 사실 이번에 처음 데이터 크롤링을 시도해보았는데 생각보다 까다로운 작업이었다. 셀레니움으로 시도하였는데 잘 되는듯 하다가도 난관에 부딛히기 일쑤였다. 시간이 꽤 오래리고 있었는데 다른 백엔드 동료는 API   

### 추천 관련 백엔드 API 명세/개발 (FastAPI)
Django, Flask, FastAPI 중에 FastAPI를 선택한 이유는 첫번째, 가볍고 (장고 탈락~) 두번째, 사용자수가 증가하고 있기 때문에 FastAPI를 선택하였다. fastAPI는 실제로 사용해보니 정말로 빠르고 가벼워서 만족도가 굉장히 높았다. 그리고 프로젝트 규모가 굉장히 작다보니 사용하기 아주 적절하지 않았나 싶다. 

## 가장 힘들었던 트러블
### 단연 환경설정 😵‍💫
이번에 파이썬 환경설정 때문에 정말 많은 나의 머리카락이 뽑혔다. 정확하게 얘기하자면 로컬에서 잘 작동하는데 우분투 서버에서 빌드가 되지 않는 현상이 문제였다.

파이썬 버전이나 다른 패키지들의 버전이 안맞는게 있어서 그런가 싶어서 문서를 찾아보고 버전을 업그레드 해보았다가, 다운그레이드도 해보았다가, 그래도 안되서 지웠다가(파이썬을 지우는 작업도 간단한 작업이 아니다.) 다시 깔아도 보고 했지만 그래도 여전히 되지는 않았다...

이 작업을 하필이면 설에 하느라 동료가 본가에 가있느라 혼자 끙끙싸맸다. 너무 안풀려서 이제 도커라이징이 잘못되었나 싶어서 주변 사람들에게도 다 물어보고 그렇게 2-3일을 씨름하다가 어떤 외국 인터넷 사이트에서 어떤 사람이 파이썬 패키지를 시스템에 깔면 안된다? 이런 말을 보고 아 설마 내 시스템 환경에 잘못 깔려있나 싶어서 내 맥에 usr안에 들어가서 파이썬 .bash_profile 이랑 .bashrc 를 뒤져보는데 환경변수에 이상한 것들이 많이 연결되어있었다. 

아하 이거구나 싶어서 어떤게 문제인가 환경변수를 하나씩 지워보면서 확인하고 있는데 어떤걸 지우니까 아얘 내 맥에 깔려있는 모든 프로그램들을 사용할 수가 없게 되었다. 심지어는 vi도 되지 않아서 파일을 수정하지도 못하는 지경에 이르렀다. 또 끙끙 싸매다가 결국 고쳐냈다. 

그렇지만 여전히 원인을 알 수가 없어서 동료의 로컬에서 시도해 보았는데 잘 안되길래 freeze > requiremets.txt를 하고 필요한 패키지들이 자동으로 깔리고 난 뒤 다시 시도해보니까 그렇게 안되어던 빌드가 잘 되는것을 확인할 수 있었다.


## 스스로 부족했다고 느끼는 부분
### 체력관리
나만무 기간에 B형 독감에 걸렸었는데 건강관리도 정말 중요하다고 느꼈다. 아무리 바빠도 하루에 30정도는 운동을 하는 동료를 보면서 체력관리를 어떻게 해야하는지 배웠다.
제일 잘 알려져있는 같은 시간에 먹고 자기가 제일 중요한데 바쁘다보니 끼니를 거르거나 야근을 하느라 잠을 줄인다거나 하면서 몸의 균형이 깨지면서 면역 시스템이 무너지는 것을 경험했다.
>action plan🔥
1. 아무리 바빠도 하루에 30분 걷거나 운동하기
2. 같은 시간에 자고 일어나기<br>
-> 위의 두가지를 지킬 수 있는 쉬운 방법!! <br>__매일 10시에 자고 5시에 일어나서, 일어나자마자 30분 산책하기!__

### 시간 / 일정 관리
정글에 들어온 뒤로 나는 ADHD증상이 심해져서 약까지 복용하고 있었지만 시간관리와 일정관리가 정말 힘들었다. 스스로 현재 중요하지 않은 일을 하고 있다는 것을 알면서도 우선순위대로 일을 처리하지 못하는 나를 보면서 자괴감이 많이 들었는데 이는 흔히 ADHD 환자가 잘 못하는 것이라고 한다.

하지만 나는 사람이 자신의 약점을 잘 알고 개선시키려는 의지가 있다면 오히려 보통 사람들보다 더 나아질 수 있다고 생각하기 때문에 나의 약점을 장점으로 가져가려 한다.

>action plan🔥
1. 아침 산책 후 오늘의 __일정 정리__하는 시간 5분 갖기(우선순위 정렬)
2. 야근 안하기 위해 __업무시간에 최대한 집중__하기
3. 아무리 일이 많아도 __9시까지 공부/일 마무리__하기  _(잘 되고 있어서 아쉽다면 다음날 계속 할 수 있는 동력이 되고, 잘 안되고 있었다면 자고 일어나면 더 잘 될것이니!)_
4. 하루 일과를 마무리하기 전에 __다음날 해야하는 일 정하기__

### F들과 피드백 주고받기
나는 ENTP/INTP 이고 T와 F가 거의 6:4 정도라서 나름 F친화적인 T라 스스로를 여겨왔지만, 업무에 있어서는 나도 몰랐던 나의 T성향이 굉장히 나오는듯 했다.

예를들어, 회의때 서로의 피드백을 주고 받을 때 나는 어떤 아이디어가 별로라고 생각되면 '이건 이런이런 이유에서 별로인것 같아요. 그보다 이렇게 하면 더 좋을 것 같은데 어떻게 생각하시나요?' 라고 나의 의견을 먼저 말하는 편이다.

T들과 소통할 때는 문제가 없었는데 이번 팀원들은 나를 제외하고 모두 F 사람들이었기에 문제가 생겼다.

어떤 팀원이 나의 피드백 방식에 상처를 조금 받았다고 말해주었다. (그 당시에는 이 정도에 상처받는다고? 어이없어 했지만 사실 말해줬다는 사실에 그 팀원에게 참 감사하다)

그래서 일단 칭찬하고 나의 의견을 조심스럽게 제시하는 쪽으로 자연스럽게 나의 소통방식이 바뀌었다. 예를들어, '오! 좋은데요? 혹시 이렇게하면 더 좋을까요?' 혹은 고개를 끄덕이며 '음~ 좋네요~' 라고 듣고 난 뒤에 조심스럽게 '좋은데 다만 우려되는 부분으로 ~게 있긴 한 것 같아요' 라고 한다던가.

이렇게 바뀐 부분은 소통에서 조금 더 시간을 잡아먹어서 생산성이 이전 방식 보다는 떨어질 수 있지만 우리는 로봇이 아니고 인간과 대화하며 일을 하기 위해서는 조금 불편하더라도 서로 존중하고 조심해야 하는게 맞는 것 같다.

이번에 나와 참 다른 성격의 팀원들을 만나서 어려운 점도 많았짐나 결국 내가 이렇게나 발전할 수 있었기에 너무 감사하다.

---
끝으로 나만무 최종발표때 정성훈 멘토님💛과 찍은 사진을 첨부한다!
![](https://velog.velcdn.com/images/gigis-note/post/67aa2880-6a57-40e4-b246-764ac0650ca7/image.jpg)
