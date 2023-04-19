#!/usr/bin/env python
# coding: utf-8

# In[ ]:import streamlit
import streamlit as st
st.set_page_config(layout='wide')
import pandas as pd
import numpy as np
import re
from graphviz import Digraph

user_input =st.text_area('enter your query here',height=200)
upload =st.button('upload')

##### data cleaning

def query_cleaning(a):
    pattern = r"--.*$"
    new_text = re.sub(pattern, " ", a, flags=re.MULTILINE)
    cleaned_query =new_text.lower()
    cleaned_query =cleaned_query.replace(' as ',' ')
#     cleaned_query =' '.join(cleaned_query.split())
    return cleaned_query

# query_list =list(user_input.split(';'))
query_list =list(user_input.split(';'))
cleaned_query_list =[]
for i in query_list:
    query_cleaned =query_cleaning(i)
    if len(query_cleaned)>10:
        cleaned_query_list.append(query_cleaned)    

##### extract table names
tables =r"(?:from|inner join|left join|right join|full join|outer join|insert into|delete from|'join ')\s+\w+\.?\w+"
table_list = pd.DataFrame(columns=['query_no', 'raw_table', 'table_name', 'table_alias_name', 'join_type'])
query =[]
table_name =[]
sl_no=0
query_no=[]
for i in cleaned_query_list:
    table_query =re.findall(tables,i)
    sl_no+=1
    for j in table_query:
        query.append(i)
        table_name.append(j)
        query_no.append(sl_no)

master_table =pd.DataFrame(query, columns=['sql_query'])
master_table['query_no']=query_no
keywords = ["delete from", "from", "left join", "right join", "inner join", "join", "insert into"]
table_name_cleaned =[]
for string in table_name:
    words = string.split()
    table_name_cleaned.append(words[-1])
master_table['table_name']=table_name_cleaned

        
       
st.write('Number of Queries',len(cleaned_query_list))
st.write('Number of Tables', master_table.shape[0])
st.write('Number of unique tables are',master_table['table_name'].nunique())
st.write('list of tables',master_table)
st.download_button('Download CSV',master_table.to_csv(),mime ='text/csv')

