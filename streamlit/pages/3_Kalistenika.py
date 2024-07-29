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

cal_all['exercise_count'] = cal_all['exercise']
cal_agg = cal_all.groupby(['exercise', granulation, 'muscle1', 'muscle2']) \
    .agg({
        'exercise_count' : 'count',
        'reps_sum':'sum'
    }) \
    .reset_index()

exercises = pd.DataFrame(st.session_state["workouts"]['exercise'].unique())
exercises.columns = ['exercise']

###############################################################################################
# first row - metrics
###############################################################################################
col11, col12, col13, col14 = st.columns(4)

with col11:
    reps = int(cal_agg['reps_sum'].sum())
    st.metric(label="Wykonane powtórzenia", value=format(reps, ',').replace(',', ' '))

with col12:
    pull_up_variations = exercises[(exercises['exercise'].str.contains('podciąganie')) & (~exercises['exercise'].str.contains('australijskie'))]['exercise'].to_list()
    reps_pullup = int(cal_agg[cal_agg['exercise'].isin(pull_up_variations)]['reps_sum'].sum())
    st.metric(label="Wykonane podciągnięcia", value=format(reps_pullup, ',').replace(',', ' '))

with col13:
    push_up_variations = exercises[(exercises['exercise'].str.contains('pompk')) | (exercises['exercise'].str.contains('diamenty'))]['exercise'].to_list()
    reps_pushup = int(cal_agg[cal_agg['exercise'].isin(push_up_variations)]['reps_sum'].sum())
    st.metric(label="Wykonane pompki", value=format(reps_pushup, ',').replace(',', ' '))

with col14:
    dip_variations = exercises[exercises['exercise'].str.contains('dip')]['exercise'].to_list()
    reps_dip = int(cal_agg[cal_agg['exercise'].isin(dip_variations)]['reps_sum'].sum())
    st.metric(label="Wykonane dipy", value=format(reps_dip, ',').replace(',', ' '))


###############################################################################################
# second row - favourite exercises and muscles
###############################################################################################
col21, col22 = st.columns(2)

cal_agg_ex = cal_agg.groupby(['exercise', 'muscle1', 'muscle2']) \
    .agg({
        'exercise_count' : 'sum',
        'reps_sum':'sum'
    }) \
    .reset_index() \
    .sort_values(by = 'exercise_count', ascending = True) \
    .tail(10)

fig_fav = px.bar(
    cal_agg_ex,
    x = "exercise_count", 
    y = "exercise",
    title = "Najczęśniej wykonywane ćwiczenia",
    orientation='h'
)
fig_fav.update_layout(
    plot_bgcolor='white',
    xaxis_title = "Liczba wystąpień",
    yaxis_title= "exercise" ,
    title_x=0.3
)

with col21:
    st.plotly_chart(fig_fav, theme="streamlit", use_container_width=True)

muscle1_agg = cal_agg_ex.groupby('muscle1').agg({'exercise_count': 'sum'}).reset_index()
muscle2_agg = cal_agg_ex.groupby('muscle2').agg({'exercise_count': 'sum'}).reset_index()
muscle_agg = pd.merge(
    left=muscle1_agg,
    right=muscle2_agg,
    left_on='muscle1',
    right_on='muscle2',
    how = 'outer'
)
muscle_agg['count'] = muscle_agg['exercise_count_x'].fillna(0) * 2 + muscle_agg['exercise_count_y'].fillna(0)
muscle_agg.loc[:, 'muscle1'] = muscle_agg['muscle1'].fillna(muscle_agg['muscle2'])
pie = px.pie(   
    muscle_agg, 
    values='count', 
    names='muscle1', 
 
)
    
with col22:
    st.plotly_chart(pie, theme="streamlit", use_container_width=True)
print(muscle_agg.head(20))

###############################################################################################
# Third row - push ups, pull ups and dips over time
###############################################################################################
col31, col32 = st.columns(2)

pull_up_variations_all = exercises[exercises['exercise'].str.contains('podciąganie')]['exercise'].to_list()
fig_pull = px.bar(
    cal_agg[cal_agg['exercise'].isin(pull_up_variations_all)],
    x = granulation, 
    y = "reps_sum",
    color='exercise', 
    #color_discrete_map=pallete, 
    title = "Wykonane powtórzenia podciągnięć",
    #hover_name=category,
    hover_data=['reps_sum', granulation]
)
fig_pull.update_layout(
    plot_bgcolor='white',
    showlegend=False,
    xaxis_title = granulation_name,
    yaxis_title= "Liczba powtórzeń" 
)

with col31:
    st.plotly_chart(fig_pull, theme="streamlit", use_container_width=True)

fig_push = px.bar(
    cal_agg[(cal_agg['exercise'].isin(push_up_variations)) | (cal_agg['exercise'].isin(dip_variations))],
    x = granulation, 
    y = "reps_sum",
    color='exercise', 
    #color_discrete_map=pallete, 
    title = "Wykonane powtórzenia pompek i dipów",
    #hover_name=category,
    hover_data=['reps_sum', granulation]
)
fig_push.update_layout(
    plot_bgcolor='white',
    showlegend=False,
    xaxis_title = granulation_name,
    yaxis_title= "Liczba powtórzeń" ,
)

with col32:
    st.plotly_chart(fig_push, theme="streamlit", use_container_width=True)