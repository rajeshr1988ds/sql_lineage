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

query_list =list(user_input.split(';'))
cleaned_query_list =[]
for i in query_list:
    query_cleaned =query_cleaning(i)
    if len(query_cleaned)>10:
        cleaned_query_list.append(query_cleaned)    


##### extract table names
tables =r"(?:from|inner join|left join|right join|full join|outer join|insert into|delete from|'join ')\s+\w+\.?\w+?\s+?(?:as\s+)?\w+"
table_list = pd.DataFrame(columns=['query_no', 'raw_table', 'table_name', 'table_alias_name', 'join_type'])
query_no = 0    
for i in cleaned_query_list:
    table_query =re.findall(tables,i)
    if len(table_query)>0:
        
        table_query =[string.replace(' where',' ') for string in table_query]
        table_query =[string.replace(' select',' ') for string in table_query]
        table_query =[string.replace(' rstrip',' ') for string in table_query]
        table_details =pd.DataFrame(table_query,columns=['raw_table'])
        table_details['raw_table']=table_details['raw_table'].str.lower()
        table_details['join_type']=table_details['raw_table'].str.split('from | join | into',expand=True)[0]
        table_details['join_type']=table_details['join_type'].apply(lambda x: x if x.startswith(('inner','left','right','delete','insert','join')) else 'from')
        table_details['table_alias_name']=table_details['raw_table'].str.split()
        table_details['table_alias_name']=table_details['table_alias_name'].apply(lambda x: x[-1])
        table_details['table_name']=table_details['raw_table'].str.split('from | join | into ',expand=True)[1]
        table_details['table_name']=table_details['table_name'].str.split(' as ',expand=True)[0]
        table_details['table_alias_name'].fillna(table_details['table_name'],inplace=True)
        table_details['table_alias_name']=table_details['table_alias_name'].str.replace(' ','')
        query_no=query_no+1
        table_details['query_no']=query_no
        table_list =pd.concat([table_list,table_details],ignore_index =True)



##### extract columns
join_conditions =r"(\S+)\s*=\s*(\S+)"
join_table =pd.DataFrame(columns =['query_no','source_column','target_column','source_table','target_table'])
query_no =0

def extract_substring(value):
    if '.' in value:
        parts = value.split('.')
        if len(parts) == 2:
            return parts[0]
        elif len(parts) >= 3:
            return '.'.join(parts[:2])
    else:
        return value
for i in range(len(cleaned_query_list)):
    table_query =re.findall(tables,cleaned_query_list[i])
    if len(table_query)>0:
        
        table_1=re.findall(join_conditions,cleaned_query_list[i])
        table_columns =pd.DataFrame(table_1,columns=['COLUMN_1','COLUMN_2'])
        table_columns['source_column']=table_columns['COLUMN_1'].apply(lambda x: x.split('.',2)[-1])
        table_columns['target_column']=table_columns['COLUMN_2'].apply(lambda x: x.split('.',2)[-1])
        table_columns['source_table']=table_columns['COLUMN_1'].apply(extract_substring)
        table_columns['target_table']=table_columns['COLUMN_2'].apply(extract_substring)
        table_columns['target_table']=table_columns['target_table'].str.replace(' ','')
        table_columns['source_table']=table_columns['source_table'].str.replace(' ','')
        query_no =query_no+1
        table_columns['query_no']=query_no
        join_table =pd.concat([join_table,table_columns],ignore_index=True)


##### create table and column table
for index, row in table_list.iterrows():
    table = row['table_alias_name']
    query = row['query_no']
    table_name = row['table_name']
    
    join_table.loc[(join_table['source_table'] == table) & (join_table['query_no'] == query), 'source_table_name'] = table_name
    join_table.loc[(join_table['target_table'] == table) & (join_table['query_no'] == query), 'target_table_name'] = table_name

join_table['query_number'] =join_table['query_no'].astype(str)
table_list['query_number']=table_list['query_no'].astype(str)
join_table['graph_source_table']= join_table['query_number'].str.cat(join_table['source_table_name'], sep='_')
join_table['graph_target_table']=join_table['query_number'].str.cat(join_table['target_table_name'], sep='_')
table_list['graph_table_name']=table_list['query_number'].str.cat(table_list['table_name'], sep='_')

# create a directed graph
dot = Digraph(comment='My Graph',
              node_attr={'shape': 'oval', 'style': 'filled', 'fontsize': '12', 'fontname': 'Arial'},
              edge_attr={'color': 'blue', 'style': 'dashed', 'fontsize': '10', 'fontname': 'Arial'},
              graph_attr={'size': '16,12'})
table_list = table_list.dropna(subset=['graph_table_name'])
join_table = join_table.dropna(subset=['graph_source_table', 'graph_target_table'])



# add a node for each unique name in the dataframe
# for name in table_list['graph_table_name'].unique():
#     dot.node(name, name)

for _, row in table_list.iterrows():
    name = row['graph_table_name']
    header = f"{row['join_type']}\n{row['graph_table_name']}"
    dot.node(name, label=header)
    
### edge
for i, row in join_table.iterrows():
    source = str(row['graph_source_table'])
    target = str(row['graph_target_table'])
    label = str(row['source_column']+ '=' + row['target_column'])
    dot.edge(source, target, label)
# render the graph as a PNG image
dot.render('my-graph', view=True)

st.write('Number of Queries',len(cleaned_query_list))

