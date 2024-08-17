# plots with all sports summed up together

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import datetime
from data_processing import filter_by_period, hour_str
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
        st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')
        #st.session_state["max_date"] = st.session_state["calendar"]['date'].max()

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
    granultaion_translation_x = {'Miesiąc' : 'month', 'Tydzień' : 'week', 'Dzień' : 'day_of_year'}
    granulation_x = granultaion_translation_x[granulation_name]
    granultaion_translation_agg = {'Miesiąc' : 'year_month', 'Tydzień' : 'year_week', 'Dzień' : 'date'}
    granulation_agg = granultaion_translation_agg[granulation_name]

    dates = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])
    if granulation_name == 'Dzień':
        dates = dates.drop(['week_day','sport','time','info','hours','minutes','seconds','total_seconds','category'], axis = 1)
    elif granulation_name == 'Tydzień':
        dates = dates.groupby(['year','week','year_week']).size().reset_index()
    else:
        dates = dates.groupby(['year','month','month_str','month_name_en','month_name_pl','year_month']).size().reset_index()

    calendar = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])
    calendar = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])
    calendar = calendar[~calendar['sport'].isna()]
    calendar = calendar[calendar['sport'] != '']
    #calendar = calendar.merge(st.session_state["sports"], on = 'sport', how = 'left')
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
        category = 'category'
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
# plots - fist row
###############################################################################################
calendar_filtered['sport_count'] = calendar_filtered['sport']
plot_data = calendar_filtered.groupby([category, granulation_agg]).agg({
    'sport_count' : 'count',
    'total_seconds' : 'sum'
}).reset_index()
plot_data['hours'] = np.round(plot_data['total_seconds'] / 3600, 2)
plot_data['hours_str'] = plot_data['total_seconds'].apply(lambda x : hour_str(x))
plot_data = plot_data.merge(
    right = dates,
    on = granulation_agg,
    how='right'
)
#plot_data.loc[:, 'sport_count'] = plot_data['sport_count'].fillna(0)
plot_data.loc[:, 'sport'] = plot_data['sport'].fillna('')

col11, col12, col13 = st.columns([1,2,2])

with col11:
    metric_data = plot_data['sport_count'].sum()
    st.metric(label="Łączna liczba treningów", value=int(metric_data))

with col12:
    training_time = plot_data['total_seconds'].sum()
    h, m,s =  int(training_time // 3600), int((training_time % 3600) // 60), int(training_time % 60)
    st.metric(label="Łączny czas treningów", value=f"{h} godzin {m} minut {s} sekund")

with col13:
    if metric_data == 0:
        avg_time = 0
    else:
        avg_time = training_time / metric_data
    h_avg, m_avg, s_avg =  int(avg_time // 3600), int((avg_time % 3600) // 60), int(avg_time % 60)
    st.metric(label="Średi czas treningu", value=f"{h_avg} godzin {m_avg} minut {s_avg} sekund")

###############################################################################################
# plots - second row
###############################################################################################
col21, col22 = st.columns(2)

with col21:
    fig = px.bar(plot_data,
        x = granulation_x, 
        y = "sport_count",
        color=category, 
        color_discrete_map=pallete, 
        hover_name=category,
        hover_data=['sport_count', granulation_x]
    )

    fig.update_layout(
        plot_bgcolor='white',
        showlegend=False,
        xaxis_title = granulation_name,
        yaxis_title= "Liczba treningów" ,
        title = "Liczba treningów w przedziale czasowym",
        #margin=dict(l=20, r=30, t=10, b=20),
    )
    
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with col22:
    pie = px.pie(
        plot_data, 
        values='sport_count', 
        names=category, 
        color=category,  
        color_discrete_map=pallete,
    )

    pie.update_layout(
        title= "Procentowy udział sportów w treningach"
    )
    
    st.plotly_chart(pie, theme="streamlit", use_container_width=True)


###############################################################################################
# plots - third row
###############################################################################################
col31, col32 = st.columns(2)

with col31:
    fig_count = px.bar(
        plot_data,
        x = granulation_x, 
        y = "hours",
        color=category, 
        color_discrete_map=pallete, 
        hover_name=category,
        hover_data=['hours_str', granulation_x]
    )

    fig_count.update_layout(
        plot_bgcolor='white',
        showlegend=False,
        xaxis_title = granulation_name,
        yaxis_title= "Czas treningów" ,
        title = "Czas treningów w przedziale czasowym",
        #margin=dict(l=20, r=30, t=10, b=20),
    )
    
    st.plotly_chart(fig_count, theme="streamlit", use_container_width=True)

with col32:
    pie_time = px.pie(
        plot_data, 
        values='hours', 
        names=category, 
        color=category,  
        color_discrete_map=pallete,
        #hover_data='hours_str'
    )

    pie_time.update_traces(
        hovertemplate = "%{label}: %{percent}"
    )

    pie_time.update_layout(
        title = "Procentowy udział czasu uprawaniu sportów",
    )

    st.plotly_chart(pie_time, theme="streamlit", use_container_width=True)

    