# gym

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

chosen_columns = ['date', 'sport', 'exercise', 'details', 'comments']
w = st.session_state["workouts"][chosen_columns]

exercises = w['exercise'].unique()
multiselect = st.selectbox(
    label="Wybierz ćwiczenie",
    options=exercises
)

rows = st.number_input(label = "Ile ostatnich rekordów chcesz zobaczyć?", min_value=0, max_value=None, value=5, step=1)

w.loc[:, 'comments'] = w['comments'].fillna('')
w = w.groupby(chosen_columns).size().reset_index()[chosen_columns]
result = w[w['exercise'] == multiselect].sort_values(by = 'date', ascending = False).reset_index(drop = True)
st.table(result.head(min(result.shape[0], rows)))
