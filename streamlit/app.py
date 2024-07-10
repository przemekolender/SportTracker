import sys
sys.path.append("data")
import os
import streamlit as st
import pandas as pd
import altair as alt
#import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap
import calplot
import datetime

from data_processing import run_distance, run_time, reps_sum, kilos_sum, best_weight, most_reps, create_date_dim, filter_by_period




st.set_page_config(
    page_title="SportTracker",
    page_icon="🏋️‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("workouts.csv")

if "date_dim" not in st.session_state:
    st.session_state["date_dim"] = create_date_dim(st.session_state["workouts"]['date'])

if "min_date" not in st.session_state:
    st.session_state["min_date"] = st.session_state["date_dim"]['date'].min()

if "max_date" not in st.session_state:
    st.session_state["max_date"] = st.session_state["date_dim"]['date'].max()

with st.sidebar:
    st.title('🏋️‍♀️ SportTracker')
    
    year_list = list(st.session_state["date_dim"]['year'].unique())[::-1]
    selected_year = st.selectbox('Wybierz rok', ['-'] + year_list, index=len(year_list)-1)

    month_list = list(st.session_state["date_dim"][st.session_state["date_dim"]['year'] == selected_year]['month_name'].unique())
    selected_month = st.selectbox('Wybierz miesiąc', ['-'] + month_list)

    if selected_year == '-' and selected_month == '-':
        st.session_state["min_date"] = st.session_state["date_dim"]['date'].min()
        st.session_state["max_date"] = st.session_state["date_dim"]['date'].max()

    elif selected_year != '-' and selected_month == '-':
        st.session_state["min_date"] = f"{selected_year}-01-01"
        st.session_state["max_date"] = f"{selected_year}-12-31"

    else:
        selected_month_num = st.session_state["date_dim"][st.session_state["date_dim"]["month_name"] ==  selected_month]['month_str'].unique()[0]
        min_day = '01'
        max_day = st.session_state["date_dim"][st.session_state["date_dim"]["month_name"] ==  selected_month]['day_num'].unique()[0]

        st.session_state["min_date"] = f"{selected_year}-{selected_month_num}-{min_day}"
        st.session_state["max_date"] = f"{selected_year}-{selected_month_num}-{max_day}"



workouts = filter_by_period(st.session_state["workouts"], 'date', st.session_state["min_date"], st.session_state["max_date"])

distnace = run_distance(workouts)
st.metric(label="Total run distnace", value=f"{distnace} km")

h,m,s = run_time(workouts)
st.metric(label="Total run time", value=f"{h} hours {m} minutes {s} seconds")

reps = reps_sum(workouts)
st.metric(label="Total reps", value=reps)

kilos = kilos_sum(workouts)
st.metric(label="Total kilos lifted", value=kilos)

max_weight, max_weight_reps = best_weight(workouts, 'wyciskanie na ławce płaskiej')
st.metric(label="Best bench press", value=max_weight, delta=max_weight_reps, delta_color='off')

max_reps = most_reps(workouts, 'podciąganie nachwytem')
st.metric(label="Most pull ups", value=max_reps)
