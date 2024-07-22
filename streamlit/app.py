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
import plotly.express as px
import plotly.graph_objects as go

from data_processing import run_distance, run_time, reps_sum, kilos_sum, best_weight, most_reps, create_date_dim, filter_by_period
from calenda_heatmap import month_workout_number
from palletes import *


st.set_page_config(
    page_title="SportTracker",
    page_icon="🏋️‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv")

if "calendar" not in st.session_state:
    st.session_state["calendar"] = pd.read_csv("files/calendar.csv")

if "date_dim" not in st.session_state:
    st.session_state["date_dim"] = create_date_dim(st.session_state["calendar"]['date'])

if "min_date" not in st.session_state:
    st.session_state["min_date"] = st.session_state["date_dim"]['date'].min()

if "max_date" not in st.session_state:
    st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')



###############################################################################################
# draw calendar
###############################################################################################
sports = pd.read_csv("files/sports.csv")
c = st.session_state["calendar"].merge(sports, on='sport', how = 'left')
c['sport'] = c['sport'].fillna('')
c['kategoria'] = c['kategoria'].fillna('')


st.markdown("# Kalendarz treningów")

with st.sidebar:
    calndar_type = st.radio(
        'Rodzaje sportów',
        ['Wszystkie', 'Kategorie', 'Bieganie i sporty siłowe', 'Ogólne aktywności']
    )

if calndar_type == 'Wszystkie':
    color = c['sport'].apply(lambda x : sport_color[x])

elif calndar_type == 'Kategorie':
    color = c['kategoria'].apply(lambda x : sport_category_color[x])

elif calndar_type == 'Bieganie i sporty siłowe':
    color =  c['sport'].apply(lambda x : run_work[x])

elif calndar_type == 'Ogólne aktywności':
    color = c['sport'].apply(lambda x : event_color[x])

fig = go.Figure(go.Scatter(
    x=c['week'], 
    y=c['day_of_week_name_pl'], 
    text=c['info'],
    hoverinfo = 'text',
    mode='markers', 
    marker = dict(size=13, symbol='square', color = color)
))
fig.update_yaxes(categoryorder='array', categoryarray= ['Niedziela', 'Sobota', 'Piątek', 'Czwartek', 'Środa', 'Wtorek', 'Poniedziałek'])
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title = 'Tydzień',
    yaxis_title=None   
)

st.plotly_chart(fig, use_container_width=True)



###############################################################################################
# draw metrics
###############################################################################################
workouts = filter_by_period(st.session_state["workouts"], 'date', st.session_state["min_date"], st.session_state["max_date"])


st.markdown("## Rekordy w kalistenice")
col11, col12, col13, col14 = st.columns(4)

with col11:
    max_reps = most_reps(workouts, 'podciąganie nachwytem')
    st.metric(label="Najwięcej podciągnięć nachwytem", value=max_reps)
   
with col12:
    max_reps = most_reps(workouts, 'dipy')
    st.metric(label="Najwięcej dipów", value=max_reps)
   
with col13:
    max_reps = most_reps(workouts, 'pompki')
    st.metric(label="Najwięcej pompek", value=max_reps)

with col14:
    max_reps = most_reps(workouts, 'muscle up')
    st.metric(label="Najwięcej muscleupów", value=max_reps)


st.markdown('## Rekory na siłowni')
col21, col22, col23, col24 = st.columns(4)

with col21:
    max_weight, max_weight_reps = best_weight(workouts, 'wyciskanie na ławce płaskiej')
    st.metric(label="Wyciskanie", value=max_weight, delta=max_weight_reps, delta_color='off')

with col22:
    max_weight, max_weight_reps = best_weight(workouts, 'przysiady')
    st.metric(label="Przysiad", value=max_weight, delta=max_weight_reps, delta_color='off')

with col23:
    max_weight, max_weight_reps = best_weight(workouts, 'martwy ciąg')
    st.metric(label="Martwy ciąg", value=max_weight, delta=max_weight_reps, delta_color='off')

with col24:
    max_weight, max_weight_reps = best_weight(workouts, 'ohp')
    st.metric(label="OHP", value=max_weight, delta=max_weight_reps, delta_color='off')

