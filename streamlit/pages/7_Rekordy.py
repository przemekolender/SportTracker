# best results of exercises

import streamlit as st
import pandas as pd
import altair as alt
from data_processing import best_weight, most_reps, best_run_approx, filter_by_period
 

st.set_page_config(
    page_title="Ostatnie wyniki", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Rekordy")

alt.themes.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|')

chosen_columns = ['date', 'sport', 'exercise', 'details', 'comments', 'reps', 'weight', 'distance_km', 'run_hours', 'run_minutes', 'run_seconds', 'run_total_seconds', 'muscle1', 'description']
w = st.session_state["workouts"][chosen_columns]


###############################################################################################
# weight records
###############################################################################################
st.markdown("### Rekordy podniesionego ciężaru")

w['description'] = w['description'].fillna('') 
exercises = w.loc[(~w['description'].str.contains('na czas') ) & (w['muscle1'] != 'bieganie'), 'exercise'].unique()
exercise_weight = st.multiselect(
    label="Wybierz ćwiczenie",
    options=exercises,
    placeholder="", 
    key=1
)

if len(exercise_weight) > 0:
    bw_d = {}
    for bw_ex in exercise_weight:
        bw_weight, bw_reps = best_weight(w, bw_ex)
        bw_d[bw_ex] = [bw_weight, bw_reps]
    
    bw_df = pd.DataFrame(bw_d).T
    bw_df.columns = ['Ciężar', 'Liczba powtórzeń']
    bw_df['Ciężar'] = bw_df['Ciężar'].astype(float).round(2).astype(str) + ' kg'
    bw_df['Liczba powtórzeń'] = bw_df['Liczba powtórzeń'].astype(int)
    
    st.table(bw_df)


###############################################################################################
# reps records
###############################################################################################
st.markdown("### Rekordy liczy powtórzeń")

exercise_reps = st.multiselect(
    label="Wybierz ćwiczenie",
    options=exercises,
    placeholder="",
    key=2
)

if len(exercise_reps) > 0:
    br_d = {}
    for br_ex in exercise_reps:
        br_reps = most_reps(w, br_ex)
        br_d[br_ex] = [br_reps]
    
    br_df = pd.DataFrame(br_d).T
    br_df.columns = ['Liczba powtórzeń']
    br_df['Liczba powtórzeń'] = br_df['Liczba powtórzeń'].astype(int)
    
    st.table(br_df)


###############################################################################################
# run records
###############################################################################################
st.markdown("### Rekordy w bieganiu")

distance = st.number_input(
    label = "Rekord na jakim dystansie chcesz zobaczyć?", 
    min_value=0.0, 
    max_value=None, 
    value=None, 
    step=0.1
)

if distance is not None:
    best_run = best_run_approx(w, distance)
    best_run.columns = ['data', 'dystans', 'tempo', 'czas']
    best_run['dystans'] = best_run['dystans'].astype(float).round(2).astype(str)
    st.table(best_run)
