# gym

import streamlit as st
import pandas as pd
import altair as alt
import datetime
from data_processing import filter_by_period
import plotly.express as px
from palletes import *
 

st.set_page_config(
    page_title="Siłownia", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Treningi na siłowni")

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
gym_all = workouts[workouts['sport'] == 'siłownia']

if ignore_empty:
    gym_all = gym_all.merge(
        right = calendar,
        on = 'date',
        how = 'right'
    )
    gym_all['reps_sum'] = gym_all['reps_sum'].fillna(0)
    gym_all['weight'] = gym_all['weight'].fillna(0)
    gym_all['weights_lifted'] = gym_all['weights_lifted'].fillna(0)

else:
    gym_all = gym_all.merge(
        right = calendar,
        on = 'date',
        how = 'inner'
    )

gym_agg = gym_all.groupby([granulation]) \
    .agg({
        'reps_sum':'sum',
        'weight':'sum',
        'weights_lifted':'sum'
    }) \
    .reset_index()


###############################################################################################
# first row - metrics
###############################################################################################
col11, col12 = st.columns(2)

with col11:
    reps = int(gym_all['reps_sum'].sum())
    st.metric(label="Wykonane powtórzenia", value=format(reps, ',').replace(',', ' '))

with col12:
    weight = int(gym_all['weights_lifted'].sum())
    st.metric(label="Podniesiony ciężar", value=f"{format(weight, ',').replace(',', ' ')} kg")

###############################################################################################
# second row - favourite exercises and muscles
###############################################################################################
col21, col22 = st.columns(2)

gym_ex_agg_temp = gym_all.groupby(['exercise', 'date']) \
    .agg({
        'reps_sum':'sum',
        'weight':'sum',
        'weights_lifted':'sum'
    }) \
    .reset_index()

gym_ex_agg_temp['exercise2'] = gym_ex_agg_temp['exercise']

gym_ex_agg = gym_ex_agg_temp.groupby(['exercise']) \
    .agg({
        'exercise2' : 'count',
        'reps_sum':'sum',
        'weight':'sum',
        'weights_lifted':'sum'
    }) \
    .reset_index() \
    .sort_values('exercise2', ascending = True) \
    .tail(10)


fig_fav = px.bar(
    gym_ex_agg,
    x = "exercise2", 
    y = "exercise",
    title = "Najczęśniej wykonywane ćwiczenia",
    orientation='h'
)
fig_fav.update_layout(
    plot_bgcolor='white',
    xaxis_title = "Liczba wystąpień",
    yaxis_title= "Ćwiczenie" ,
    title_x=0.3
)

with col21:
    st.plotly_chart(fig_fav, theme="streamlit", use_container_width=True)




###############################################################################################
# third row - reps and weight over time
###############################################################################################
col31, col32 = st.columns(2)

fig_reps = px.area(
    gym_agg, 
    x = granulation, 
    y = 'reps_sum', 
    line_shape='spline', 
    markers=True
)
fig_reps.update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*gym_agg['reps_sum'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Wykonane powtórzenia" 
)

with col31:
    st.plotly_chart(fig_reps, theme="streamlit", use_container_width=True)


fig_weight = px.area(
    gym_agg, 
    x = granulation, 
    y = 'weights_lifted', 
    line_shape='spline', 
    markers=True
)
fig_weight.update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*gym_agg['weights_lifted'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Podniesiony ciężar" 
)

with col32:
    st.plotly_chart(fig_weight, theme="streamlit", use_container_width=True)


###############################################################################################
# fourth row - bench and ohp scatters
###############################################################################################
col41, col42 = st.columns(2)

bench = gym_all[gym_all['exercise'] == 'wyciskanie na ławce płaskiej']
fig_bench = px.scatter(
    bench, 
    x = 'reps_sum', 
    y = 'weight'
)
fig_bench.update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*bench['weight'].max()],
    xaxis_title = "Liczba powtórzeń",
    yaxis_title= "Waga" ,
    title = "Wyciskanie",
    title_x=0.5
)

with col41:
    st.plotly_chart(fig_bench, theme="streamlit", use_container_width=True)


ohp = gym_all[(gym_all['exercise'] == 'ohp') | (gym_all['exercise'] == 'martwy + ohp')]
fig_ohp = px.scatter(
    ohp, 
    x = 'reps_sum', 
    y = 'weight'
)
fig_ohp.update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*ohp['weight'].max()],
    xaxis_title = "Liczba powtórzeń",
    yaxis_title= "Waga" ,
    title = "Ohp",
    title_x=0.5
)

with col42:
    st.plotly_chart(fig_ohp, theme="streamlit", use_container_width=True)

###############################################################################################
# fifth row - deadlist and squat scatters
###############################################################################################
col51, col52 = st.columns(2)

squat = gym_all[gym_all['exercise'] == 'przysiady']
fig_squat = px.scatter(
    squat, 
    x = 'reps_sum', 
    y = 'weight'
)
fig_squat.update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*squat['weight'].max()],
    xaxis_title = "Liczba powtórzeń",
    yaxis_title= "Waga" ,
    title = "Przysiady",
    title_x=0.5
)

with col51:
    st.plotly_chart(fig_squat, theme="streamlit", use_container_width=True)


deadlift = gym_all[(gym_all['exercise'] == 'martwy ciąg') | (gym_all['exercise'] == 'martwy + ohp')]
fig_deadlift = px.scatter(
    deadlift, 
    x = 'reps_sum', 
    y = 'weight'
)
fig_deadlift.update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*deadlift['weight'].max()],
    xaxis_title = "Liczba powtórzeń",
    yaxis_title= "Waga" ,
    title = "Martwy ciąg",
    title_x=0.5
)

with col52:
    st.plotly_chart(fig_deadlift, theme="streamlit", use_container_width=True)
