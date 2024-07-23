# plots with all sports summed up together

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import datetime
from data_processing import filter_by_period
import plotly.express as px
from palletes import *


st.set_page_config(
    page_title="Podsumowanie", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Podsumowanie wszystkich treningów")

alt.themes.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv")

if "calendar" not in st.session_state:
    st.session_state["calendar"] = pd.read_csv("files/calendar.csv")

if "sports" not in st.session_state:
    st.session_state["sports"] = pd.read_csv("files/sports.csv")

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
        st.session_state["max_date"] = st.session_state["calendar"]['date'].max()

    elif selected_year != '-' and selected_month == '-':
        st.session_state["min_date"] = f"{selected_year}-01-01"
        st.session_state["max_date"] = f"{selected_year}-12-31"

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


    calendar = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])
    calendar = calendar[~calendar['sport'].isna()]
    calendar = calendar.merge(st.session_state["sports"], on = 'sport', how = 'left')
    calendar_filtered = calendar
    category = 'sport'
    pallete = sport_color

    calndar_type = st.radio(
        'Rodzaje sportów',
        ['Wszystkie', 'Kategorie', 'Bieganie i sporty siłowe', 'Własny wybór']
    )

    if calndar_type == 'Wszystkie':
        calendar_filtered = calendar
        category = 'sport'
        pallete = sport_color

    elif calndar_type == 'Kategorie':
        calendar_filtered = calendar
        category = 'kategoria'
        pallete = sport_category_color

    elif calndar_type == 'Bieganie i sporty siłowe':
        calendar_filtered = calendar[calendar['sport'].isin(['bieganie', 'siłownia', 'kalistenika'])]
        category = 'sport'
        pallete = run_work

    elif calndar_type == 'Własny wybór':
        with st.sidebar:
            multiselect = st.multiselect(
                label="Wybierz sporty",
                options=calendar['sport'].unique()
            )
        calendar_filtered = calendar[calendar['sport'].isin(multiselect)]
        category = 'sport'
        pallete = sport_color


###############################################################################################
# draw plots
###############################################################################################
plot_data = calendar_filtered[[category,granulation]] \
    .groupby(by = [category, granulation]) \
    .size() \
    .reset_index(name='counts')

metric_data = plot_data['counts'].sum()
st.metric(label="Łączna liczba treningów", value=metric_data)

col11, col12 = st.columns(2)

with col11:
    fig = px.bar(plot_data,
        x = granulation, 
        y = "counts",
        color=category, 
        color_discrete_map=pallete, 
        title = None,
        hover_name=category,
        hover_data=['counts', granulation]
    )

    fig.update_layout(
        plot_bgcolor='white',
        showlegend=False,
        xaxis_title = granulation_name,
        yaxis_title= "Liczba treningów" ,
        margin=dict(l=20, r=30, t=10, b=20),
    )
    
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with col12:
    pie = px.pie(
        plot_data, 
        values='counts', 
        names=category, 
        color=category,  
        color_discrete_map=pallete
    )
    
    st.plotly_chart(pie, theme="streamlit", use_container_width=True)

#with col13:
#    metric_data = plot_data['counts'].sum()
#    st.metric(label="Łączna liczba treningów", value=metric_data)