# running

import streamlit as st
import altair as alt
import datetime
import pandas as pd
from data_processing import filter_by_period, transpose_runs
import plotly.express as px
import plotly.graph_objects as go
from palletes import *

st.set_page_config(
    page_title="Bieganie", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Bieganie")

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


workouts = filter_by_period(
    st.session_state["workouts"],
    'date',
    st.session_state['min_date'],
    st.session_state['max_date']
)
calendar = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])
runs_all = workouts[workouts['sport'] == 'bieganie']
if ignore_empty:
    runs_all = runs_all.merge(
        right = calendar,
        on = 'date',
        how = 'right'
    )
    runs_all['distance_km'] = runs_all['distance_km'].fillna(0)
    runs_all['run_hours'] = runs_all['run_hours'].fillna(0)
    runs_all['run_minutes'] = runs_all['run_minutes'].fillna(0)
    runs_all['run_seconds'] = runs_all['run_seconds'].fillna(0)
    runs_all['run_total_seconds'] = runs_all['run_total_seconds'].fillna(0)

else:
    runs_all = runs_all.merge(
        right = calendar,
        on = 'date',
        how = 'inner'
    )



runs = runs_all.groupby([granulation]) \
    .agg({
        'distance_km':'sum',
        'run_hours':'sum',
        'run_minutes':'sum',
        'run_seconds':'sum',
        'run_total_seconds':'sum'
    }) \
    .reset_index()


###############################################################################################
# first row - metrics
###############################################################################################
col11, col12 = st.columns(2)

with col11:
    distnace = float(runs['distance_km'].sum()).__round__(2)
    st.metric(label="Przebiegnięty dystans", value=f"{distnace} km")

with col12:
    seconds_full = runs['run_total_seconds'].sum()
    h, m,s =  int(seconds_full // 3600), int((seconds_full % 3600) // 60), int(seconds_full % 60)
    st.metric(label="Czas biegania", value=f"{h} godzin {m} minut {s} sekund")


###############################################################################################
# second row, km and time
###############################################################################################
col21, col22 = st.columns(2)

fig_distance = px.area(
    runs, 
    x = granulation, 
    y = 'distance_km', 
    line_shape='spline', 
    markers=True
)
fig_distance.update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*runs['distance_km'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Przebiegnięty dystans" ,
)

runs['h'] = runs['run_total_seconds'] / 3600
fig_time = px.area(
    runs, 
    x = granulation, 
    y = 'h', 
    line_shape='spline', 
    markers=True
)
fig_time.update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*runs['h'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Czas biegania" ,
)

with col21:
    st.plotly_chart(fig_distance, theme="streamlit", use_container_width=True)

with col22:
    st.plotly_chart(fig_time, theme="streamlit", use_container_width=True)


###############################################################################################
# third row, pace
###############################################################################################

runs_t = transpose_runs(runs_all)
runs_t['h'] = runs_t['run_total_seconds'] / 3600
fig_scatter = px.scatter(
    runs_t, 
    x = 'h', 
    y = 'distance_km',
    trendline='lowess',
    trendline_color_override='lightblue'
)
fig_scatter.add_trace(
    go.Scatter(
        x=[0, 1, 2, 3],
        y=[0, 12, 24, 36],
        mode="lines",
        line=go.scatter.Line(color="palevioletred", dash='dash'),
        showlegend=False
    )
)
fig_scatter.update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*runs_all['distance_km'].max()],
    xaxis_title = "Czas biegania",
    yaxis_title= "Dystans" ,
)


st.plotly_chart(fig_scatter, theme="streamlit", use_container_width=True)

#runs['pace'] = runs['run_total_seconds'] / runs['distance_km'] / 60
#fig_pace = px.area(
#    runs, 
#    x = granulation, 
#    y = 'pace', 
#    line_shape='spline', 
#    markers=True
#)
#fig_pace.update_layout(
#    plot_bgcolor='white',
#    #yaxis_range=[0, 1.1*runs['distance_km'].max()],
#    xaxis_title = granulation_name,
#    yaxis_title= "Przebiegnięty dystans" ,
#)
#
#st.plotly_chart(fig_pace, theme="streamlit", use_container_width=True)