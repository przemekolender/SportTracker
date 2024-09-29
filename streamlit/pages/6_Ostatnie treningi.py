# last gym, calistenics and running workouts preseted as a table

import streamlit as st
import pandas as pd
import altair as alt
 

st.set_page_config(
    page_title="Ostatnie wyniki", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Ostatnie wyniki ćwiczeń")

alt.themes.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|')

if "counter" not in st.session_state:
    st.session_state["counter"] = 0

###############################################################################################
# options panel
###############################################################################################
def counter_plus():
    st.session_state["counter"] += 1

def counter_minus():
    st.session_state["counter"] -= 1

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    prevoius = st.button("<", use_container_width=True,  on_click=counter_minus)

with col2:
    multiselect = st.selectbox(
        label="Wybierz sport",
        label_visibility='collapsed',
        options = ['siłownia', 'kalistenika', 'bieganie'],
        index=None,
        placeholder="Wybierz sport"
    )

with col3:
    next = st.button("\\>", use_container_width=True, on_click=counter_plus)


###############################################################################################
# preparing data & drawing table
###############################################################################################
chosen_columns = ['index', 'date', 'sport', 'exercise', 'details', 'comments']

if multiselect is not None:
    # prepare dataframe to show
    w = st.session_state["workouts"].loc[st.session_state["workouts"]['sport'] == multiselect, chosen_columns]
    w['index2'] = list(range(w.shape[0]))
    w['comments'] = w['comments'].fillna('')
    w = w.groupby(chosen_columns).agg({'index2' : 'min'}).sort_values('index2').reset_index()[chosen_columns]
    
    # fix indexes to iterate easly on the dataframe
    d = {}
    u = w['index'].unique().tolist()
    for i in range(len(u)):
        d[int(u[i])] = i
    w['index'] = w['index'].apply(lambda x : d[x])

    # make sure you cannot go out of range of activities
    st.session_state['counter'] = min(0, st.session_state['counter'])
    st.session_state['counter'] = max(-(len(u)-1), st.session_state['counter'])
    
    #print table
    df_print = w.loc[w['index'] == (len(u)-1 + st.session_state['counter']), ['date', 'exercise', 'details', 'comments']].reset_index(drop = True)
    df_print.columns = ['Data', 'Ćwiczenie', 'Szczegóły', 'Komentarze']
    st.table(df_print)
