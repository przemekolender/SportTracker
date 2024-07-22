# plots with all sports summed up together

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from data_processing import run_distance, run_time, reps_sum, kilos_sum, best_weight, most_reps, create_date_dim, filter_by_period, load_calendar, data_month_workout_number
from calenda_heatmap import month_workout_number


st.set_page_config(
    page_title="Podsumowanie", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Podsumowanie wszystkich treningów")

alt.themes.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("workouts.csv")

if "calendar" not in st.session_state:
    st.session_state["calendar"] = load_calendar()

if "date_dim" not in st.session_state:
    st.session_state["date_dim"] = create_date_dim(st.session_state["calendar"]['date'])

if "min_date" not in st.session_state:
    st.session_state["min_date"] = st.session_state["date_dim"]['date'].min()

if "max_date" not in st.session_state:
    st.session_state["max_date"] = st.session_state["date_dim"]['date'].max()

with st.sidebar:
    st.title('🏋️‍♀️ SportTracker')
    
    year_list = list(st.session_state["date_dim"]['year'].unique())[::-1]
    selected_year = st.selectbox('Wybierz rok', ['-'] + year_list, index=len(year_list)-1)

    month_list = list(st.session_state["date_dim"][st.session_state["date_dim"]['year'] == selected_year]['month_name_pl'].unique())
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

calendar = load_calendar()
data_c = data_month_workout_number(calendar)
fig = month_workout_number(data_c)
st.plotly_chart(fig, theme="streamlit", use_container_width=True)