# -*- coding: utf-8 -*-
"""binary project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yGyheD4La2ppPLBmrdbous8RpWQhEUSb
"""

from key_extraction import keywordExtractor
from transformers import ElectraModel, ElectraTokenizerFast
import numpy as np
import pandas as pd

# load model and tokenizer
name = "monologg/koelectra-base-v3-discriminator"
model = ElectraModel.from_pretrained(name)
tokenizer = ElectraTokenizerFast.from_pretrained(name)

# load keywordExtractor
key = keywordExtractor(model,tokenizer,dir='files\eng_han.csv')

# load scraping_data
scraping_result = pd.read_csv('files\binaryproject.csv')
print('음식 데이터 수 : ', len(scraping_result))
print('')
scraping_result.head()

# scraping_result_2 = pd.read_parquet('/content/scraping_result.parquet')
# scraping_result_2

# target_row = scraping_result_2[scraping_result_2['isbn13'] == "9791192469546"]
# target_row

# extract keywords
docs_keywords = key.extract_keyword(scraping_result.iloc[[1]])

# result
result = pd.DataFrame(docs_keywords)
print(result)
print('키워드 추출 예시\n')
print('음식 : ', scraping_result.loc[1, 'name'])
pd.DataFrame(result.keywords.values[0])

new_data = []
for i in range(len(scraping_result)) :
  docs_keywords = key.extract_keyword(scraping_result.iloc[[i]])
  new_data.append(docs_keywords)
print(new_data)
for item in new_data:
    item['name'] = item['name'][0]  # 'name' 필드에서 대괄호를 제거합니다.
    item['keywords'] = [word for sublist in item['keywords'] for word in sublist]  # 'keywords' 리스트를 평탄화합니다.
print(new_data)
data_search = pd.DataFrame(new_data)

data_search.to_csv('data_for_search.csv', index = False)


min_count = 2
min_length = 2
doc = scraping_result.iloc[1]

print(f'음식 정보 \n \n {doc} \n \n')


raw_data = key._convert_series_to_list(doc)
print(raw_data)
print(f'1. 음식 정보를 list로 통합 -> {len(raw_data)} 개 단어')
print(f'\n \n {raw_data}.... \n \n')

keyword_list = key._extract_keywords(raw_data)
print(f'2. 형태소 분석기를 활용해 명사만을 추출 -> {len(keyword_list)} 개 단어')
print(f'\n \n {keyword_list}.... \n \n')

translated_keyword_list = key._map_english_to_korean(keyword_list)
print(f'3. 영단어를 한글로 변환(ex python -> 파이썬) -> {len(translated_keyword_list)} 개 단어')
print(f'\n \n {translated_keyword_list[:10]}.... \n \n')

refined_keyword_list = key._eliminate_min_count_words(translated_keyword_list, min_count)
print(f'4. 최소 3번이상 반복 사용되는 단어만 추출 -> {len(refined_keyword_list)} 개 단어')
print(f'\n \n {refined_keyword_list[:10]}.... \n \n')

result = list(filter(lambda x: len(x) >= min_length, refined_keyword_list))
print(f'5. 단어 길이가 최소 한개 이상인 단어만 추출 -> {len(result)} 개 단어')
print(f'\n \n {result[:10]}.... \n \n')

from pprint import pprint
doc = scraping_result.iloc[1]
print(doc)
print(f'-- 음식이름 -- \n {doc.name} \n \n')

keyword_list = key.extract_keyword_list(doc)

print(f'음식에 대한 키워드 후보 : {len(result)} 개 단어')
print(f'{result[:10]}.... \n \n')


keyword_embedding = key.create_keyword_embedding(doc)
doc_embedding = key.create_doc_embedding(doc)


co_sim_score =key._calc_cosine_similarity(doc_embedding, keyword_embedding).flatten()

keyword = dict(zip(keyword_list, co_sim_score))
sorted_keyword = sorted(keyword.items(), key=lambda k: k[1], reverse=True)

print(f'-- 키워드 추출 결과(20개 요약)--')
pprint(sorted_keyword[:20])

df = pd.read_csv("/content/data_for_search.csv")
name = df["name"].tolist()
keywords = df["keywords"].tolist()
name[:5], keywords[:5]

doc.name

# 키워드 리스트

def get_keywords_for_food(food_name, data):
    matched_row = data[data['name'] == food_name]

    if not matched_row.empty:
        keywords_str = matched_row['keywords'].values[0]
        keywords_list = eval(keywords_str)
        return keywords_list
    else:
        return None  # If there is no matching food name, return None

food_name_to_search = input()
keywords = get_keywords_for_food(food_name_to_search, df)

if keywords == 'None' :
  print("일치하는 음식이 없습니다.")

print(keywords)
df2 = pd.DataFrame(columns=['name', 'keywords'])
df2['name'] = df['name']
# 문자열 표현된 리스트를 실제 리스트로 변환
df2['keywords'] = df['keywords'].apply(eval)

# 주어진 키워드와 일치하거나 포함하는 음식명을 필터링
matched_foods = df2[df2['keywords'].apply(lambda x: any(keyword in x for keyword in keywords))]

# 상위 20개 음식명 선택 (중복 제거)
top_foods = matched_foods['name'].drop_duplicates().head(20)
excluded_food = food_name_to_search
filtered_foods = matched_foods[(matched_foods['name'] != excluded_food)]

# 상위 20개 음식명 선택 (중복 제거 후)
top_excluded_foods = filtered_foods['name'].drop_duplicates().head(20)
top_excluded_foods.tolist()