#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pandas import DataFrame, read_excel, concat
from glob import glob

outdated_Q3 = {'0.   いずれもなし／分からない', '1．上記のいずれかを購入予定である／入荷待ちである', 
               '2．iPadなどのタブレット（キーボードを用意して下さい）', 
               '3．モバイルWiFiルータ（WiMax, ポケットWiFiなど）：月50GB程度速度制限無しで使用できるもの',
               '4．自宅や寮に，光ファイバー・ケーブルテレビなど固定の高速回線が来ており，それにスマートフォンやPCをWiFiでつなぐことで動画の視聴に問題がない'
              }

answers = glob('in_data/*')
students = 'students.xlsx'

df_students = read_excel(students, dtype=str).fillna('')
df_answers = concat([read_excel(f) for f in answers])

entry_time = df_answers.columns[3]
common_id = df_answers.columns[6]
q3 = df_answers.columns[7]
q6 = df_answers.columns[10]

df_merge = df_answers[[common_id, entry_time, q3, q6]].merge(df_students)
df_merge = df_merge.sort_values(entry_time).drop_duplicates(subset=common_id, keep='last')
for c in (q3, q6):
    df_merge[c] = df_merge[c].map(lambda a: a.split('/')[0].strip() if type(a) is str else a)
df_merge[q3] = df_merge[q3].map(lambda a: '' if a in outdated_Q3 else a)
df_merge = df_merge[[common_id, q3, q6, '学部名', '学科名']]

headcount = df_students.groupby(['学部名', '学科名']).size()
n_answers = df_merge.groupby(['学部名', '学科名']).size()
ratio = DataFrame({'学生数': headcount, '回答': n_answers})
ratio = ratio.fillna({'回答': 0})
ratio['回答率'] = ratio['回答']/ratio['学生数']
ratio.to_excel('out_data/回答率.xlsx')

departments = df_merge.groupby(['学部名', '学科名'])
for s, d in departments.groups:
    df = departments.get_group((s, d)).sort_values([q6, q3])
    df.to_csv(f'out_data/{s}{d}.csv', encoding='utf_8_sig')
