# plots with all sports summed up together

import streamlit as st
import pandas as pd
import altair as alt
from data_processing import transpose_runs


st.set_page_config(
    page_title="Zawody", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Zawody")

alt.themes.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|')

if "calendar" not in st.session_state:
    st.session_state["calendar"] = pd.read_csv("files/calendar.csv", sep='|')

if "sports" not in st.session_state:
    st.session_state["sports"] = pd.read_csv("files/sports.csv", sep='|')

runs_all = st.session_state["workouts"].loc[st.session_state["workouts"]['sport'].isin(['bieganie', 'runmageddon']), :]
runs_t = transpose_runs(runs_all)

calendar = st.session_state["calendar"].loc[st.session_state["calendar"]["category"] == "zawody", ["sport", "date"]]

runs_t["date"] = pd.to_datetime(runs_t["date"], format='%Y-%m-%d')
calendar["date"] = pd.to_datetime(calendar["date"], format='%Y-%m-%d')
runs_t = runs_t.merge(
    right = calendar,
    on = 'date',
    how = 'inner'
)[["date", "sport_y", "distance_km", "pace", "time"]]

runs_t['date'] = runs_t['date'].apply(lambda x : str(x)[:10]) 
runs_t["distance_km"] = runs_t["distance_km"].astype(float).round(2).astype(str) + " km"
runs_t.columns = ['Data', "Zawody", "Dystans", "Tempo", "Czas"]

st.table(runs_t.sort_values('Data', ascending=False).reset_index(drop = True))
