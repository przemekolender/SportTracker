import sys
sys.path.append("data")
import os
import streamlit as st
import pandas as pd
import altair as alt
#import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap
import calplot

from data_processing import run_distance, run_time, reps_sum, kilos_sum, best_weight, most_reps

workouts = pd.read_csv("workouts.csv")

st.set_page_config(
    page_title="SportTracker",
    page_icon="🏋️‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

with st.sidebar:
    st.title('🏋️‍♀️ SportTracker')
    
    year_list = list(['2023', '2024'])[::-1]
    
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)

    

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
