# last gym, calistenics and running workouts preseted as a table

import streamlit as st
import pandas as pd
import altair as alt
 

st.set_page_config(
    page_title="Ostatnie treningi", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Ostatnie treningi")

alt.theme.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|').fillna('')

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
chosen_columns = ['date', 'sport', 'exercise', 'details', 'comments']

if multiselect is not None:
    # prepare dataframe to show

    if multiselect == 'bieganie':
        w = st.session_state["workouts"].loc[st.session_state["workouts"]['sport'] == multiselect, chosen_columns] \
            .sort_values('date', ascending=True) \
            .reset_index(drop = True)
        
    else:
        w = st.session_state["workouts"].loc[st.session_state["workouts"]['sport'] == multiselect, chosen_columns] \
            .reset_index() \
            .groupby(chosen_columns).agg({'index' : 'max'}).reset_index() \
            .sort_values('index', ascending=True) \
            .reset_index(drop = True)
            
    
    j = -1
    prev = w.loc[0, 'date']
    for i in range(len(w)):
        curr = w.loc[i, 'date']
        if prev != curr:
            j -= 1
        w.loc[i, 'index2'] = j
        prev = curr

    w['index2'] = w['index2'].astype(int)

    # make sure you cannot go out of range of activities
    st.session_state['counter'] = min(0, st.session_state['counter'])
    st.session_state['counter'] = max(w['index2'].min()+1, st.session_state['counter'])
    
    #print table
    df_print = w.loc[w['index2'] == (w['index2'].min() - st.session_state['counter']), ['date', 'exercise', 'details', 'comments']].reset_index(drop = True)
    df_print.columns = ['Data', 'Ćwiczenie', 'Szczegóły', 'Komentarze']
    st.table(df_print)
    st.markdown(f"Trening {-1 * w['index2'].min() + st.session_state['counter']} / {-1 * w['index2'].min()}")
