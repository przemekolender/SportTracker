# calistenics

import streamlit as st
import pandas as pd
import altair as alt
import datetime
from data_processing import filter_by_period
import plotly.express as px
from palletes import *


st.set_page_config(
    page_title="Kalistenika", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Treningi z masą ciała")

alt.themes.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv")
    st.session_state["workouts"]["date"] = pd.to_datetime(st.session_state["workouts"]["date"], format='%Y-%m-%d')

if "calendar" not in st.session_state:
    st.session_state["calendar"] = pd.read_csv("files/calendar.csv")
    st.session_state["calendar"]["date"] = pd.to_datetime(st.session_state["calendar"]["date"], format='%Y-%m-%d')

if "min_date" not in st.session_state:
    st.session_state["min_date"] = st.session_state["calendar"]['date'].min()

if "max_date" not in st.session_state:
    st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')


###############################################################################################
# sidebar options
###############################################################################################
with st.sidebar:   
    year_list = list(st.session_state["calendar"]['year'].unique())[::-1]
    selected_year = st.selectbox('Wybierz rok', ['-'] + year_list, index=len(year_list)-1)

    month_list = list(st.session_state["calendar"][st.session_state["calendar"]['year'] == selected_year]['month_name_pl'].unique())
    selected_month = st.selectbox('Wybierz miesiąc', ['-'] + month_list)

    if selected_year == '-' and selected_month == '-':
        st.session_state["min_date"] = st.session_state["calendar"]['date'].min()
        #st.session_state["max_date"] = st.session_state["calendar"]['date'].max()
        st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')


    elif selected_year != '-' and selected_month == '-':
        st.session_state["min_date"] = f"{selected_year}-01-01"
        #st.session_state["max_date"] = f"{selected_year}-12-31"
        st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')

    else:
        selected_month_num = st.session_state["calendar"][st.session_state["calendar"]["month_name_pl"] ==  selected_month]['month_str'].unique()[0]
        min_day = '01'
        max_day = st.session_state["calendar"][st.session_state["calendar"]["month_name_pl"] ==  selected_month]['day_num'].unique()[0]

        st.session_state["min_date"] = f"{selected_year}-{selected_month_num}-{min_day}"
        st.session_state["max_date"] = f"{selected_year}-{selected_month_num}-{max_day}"


    granulation_name = st.radio(
        label="Wybierz granulację",
        options=['Miesiąc', 'Tydzień', 'Dzień']
    )
    granultaion_translation = {'Miesiąc' : 'month', 'Tydzień' : 'week', 'Dzień' : 'day_of_year'}
    granulation = granultaion_translation[granulation_name]

    ignore_empty = st.checkbox(
        label = "Czy brać pod uwagę dni bez treningów"
    )

###############################################################################################
# preparing data
###############################################################################################
workouts = filter_by_period(
    st.session_state["workouts"],
    'date',
    st.session_state['min_date'],
    st.session_state['max_date']
)

calendar = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])
cal_all = workouts[workouts['sport'] == 'kalistenika']

if ignore_empty:
    cal_all = cal_all.merge(
        right = calendar,
        on = 'date',
        how = 'right'
    )
    cal_all['reps_sum'] = cal_all['reps_sum'].fillna(0)

else:
    cal_all = cal_all.merge(
        right = calendar,
        on = 'date',
        how = 'inner'
    )

cal_agg = cal_all.groupby(['exercise', granulation]) \
    .agg({
        'reps_sum':'sum'
    }) \
    .reset_index()

exercises = pd.read_csv("files/exercises.csv")


###############################################################################################
# first row - metrics
###############################################################################################
col11, col12, col13, col14 = st.columns(4)

with col11:
    reps = int(cal_agg['reps_sum'].sum())
    st.metric(label="Wykonane powtórzenia", value=format(reps, ',').replace(',', ' '))

with col12:
    pull_up_variations = exercises[(exercises['ćwiczenie'].str.contains('podciąganie')) & (~exercises['ćwiczenie'].str.contains('australijskie'))]['ćwiczenie'].to_list()
    reps_pullup = int(cal_agg[cal_agg['exercise'].isin(pull_up_variations)]['reps_sum'].sum())
    st.metric(label="Wykonane podciągnięcia", value=format(reps_pullup, ',').replace(',', ' '))

with col13:
    push_up_variations = exercises[(exercises['ćwiczenie'].str.contains('pompk')) | (exercises['ćwiczenie'].str.contains('diamenty'))]['ćwiczenie'].to_list()
    reps_pushup = int(cal_agg[cal_agg['exercise'].isin(push_up_variations)]['reps_sum'].sum())
    st.metric(label="Wykonane pompki", value=format(reps_pushup, ',').replace(',', ' '))

with col14:
    dip_variations = exercises[exercises['ćwiczenie'].str.contains('dip')]['ćwiczenie'].to_list()
    reps_dip = int(cal_agg[cal_agg['exercise'].isin(dip_variations)]['reps_sum'].sum())
    st.metric(label="Wykonane dipy", value=format(reps_dip, ',').replace(',', ' '))

