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
        if selected_year == datetime.datetime.today().year:
            st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')
        else:
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
    granultaion_translation_hover = {'Miesiąc' : 'month_name_pl', 'Tydzień' : 'week_start_end', 'Dzień' : 'date'}
    granulation_hover = granultaion_translation_hover[granulation_name]
    granultaion_translation_agg = {'Miesiąc' : 'year_month', 'Tydzień' : 'year_week', 'Dzień' : 'date'}
    granulation_agg = granultaion_translation_agg[granulation_name]

    dates = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])
    if granulation_name == 'Dzień':
        dates = dates.drop(['week_day','sport','time','info','hours','minutes','seconds','total_seconds','category'], axis = 1)
    elif granulation_name == 'Tydzień':
        dates = dates.groupby(['year','week','year_week', 'week_start_date', 'week_end_date']).size().reset_index()
        dates['week_start_end'] = dates['week_start_date'].astype(str) + ' - ' + dates['week_end_date'].astype(str)
        dates.columns = ['year','week','year_week', 'date', 'week_end_date', 'size', 'week_start_end']
    else:
        dates = dates.groupby(['year','month','month_str','month_name_en','month_name_pl','year_month', 'fake_month_date']).size().reset_index()
        dates.columns = ['year','month','month_str','month_name_en','month_name_pl','year_month', 'date', 'size']


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

# merge with calendar to have date info

cal_all = cal_all.merge(
    right = calendar,
    on = 'date',
    how = 'right'
)
cal_all['reps_sum'] = cal_all['reps_sum'].fillna(0)

cal_all['muscle1'] = cal_all['muscle1'].fillna('')
cal_all['muscle2'] = cal_all['muscle2'].fillna('')

# grouping splitted row of 1 exercise if different weights were used

cal_all = cal_all.groupby(['exercise', 'date', 'muscle1', 'muscle2', 'year_month', 'year_week']) \
    .agg({
        'reps_sum':'sum'
    }) \
    .reset_index()


# grouping by granutlation period
cal_all['exercise_count'] = cal_all['exercise']
cal_agg = cal_all.groupby(['exercise', granulation_agg, 'muscle1', 'muscle2']) \
    .agg({
        'exercise_count' : 'count',
        'reps_sum':'sum'
    }) \
    .reset_index()

cal_agg = cal_agg.merge(
    right = dates,
    on = granulation_agg,
    how = 'right'
)


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
    pull_up_variations = exercises[(exercises['exercise'].str.contains('podciąganie')) & (~exercises['exercise'].str.contains('australijskie', na=False))]['exercise'].to_list()
    reps_pullup = int(cal_agg[cal_agg['exercise'].isin(pull_up_variations)]['reps_sum'].sum())
    st.metric(label="Wykonane podciągnięcia", value=format(reps_pullup, ',').replace(',', ' '))

with col13:
    push_up_variations = exercises[(exercises['exercise'].str.contains('pompk')) | (exercises['exercise'].str.contains('diamenty'))]['exercise'].to_list()
    reps_pushup = int(cal_agg[cal_agg['exercise'].isin(push_up_variations)]['reps_sum'].sum())
    st.metric(label="Wykonane pompki", value=format(reps_pushup, ',').replace(',', ' '))

with col14:
    dip_variations = exercises[exercises['exercise'].str.contains('dip', na=False)]['exercise'].to_list()
    reps_dip = int(cal_agg[cal_agg['exercise'].isin(dip_variations)]['reps_sum'].sum())
    st.metric(label="Wykonane dipy", value=format(reps_dip, ',').replace(',', ' '))


###############################################################################################
# second row - favourite exercises and muscles
###############################################################################################
col21, col22 = st.columns(2)

# group exercises to sum all apperances, without periods
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
    color_discrete_sequence=px.colors.sequential.Sunset_r, 
    orientation='h',
    custom_data=['exercise', 'exercise_count']
).update_layout(
    plot_bgcolor='white',
    xaxis_title = "Liczba wystąpień",
    yaxis_title= "Ćwiczenie" ,
    title_x=0.3,
    title = "Najczęśniej wykonywane ćwiczenia",
).update_traces(
    hovertemplate = "<b>%{customdata[0]}</b><br>" + "Liczba wystąpieć ćwiczenia: %{customdata[1]}<br>" + "<extra></extra>"
)

with col21:
    st.plotly_chart(fig_fav, theme="streamlit", use_container_width=True)

muscle1_agg = cal_agg_ex.groupby('muscle1').agg({'exercise_count': 'sum'}).reset_index()
muscle2_agg = cal_agg_ex[cal_agg_ex['muscle2'] != ''].groupby('muscle2').agg({'exercise_count': 'sum'}).reset_index()
muscle_agg = pd.merge(
    left=muscle1_agg,
    right=muscle2_agg,
    left_on='muscle1',
    right_on='muscle2',
    how = 'outer'
)
muscle_agg['count'] = muscle_agg['exercise_count_x'].fillna(0) * 2 + muscle_agg['exercise_count_y'].fillna(0)
muscle_agg.loc[:, 'muscle1'] = muscle_agg['muscle1'].fillna(muscle_agg['muscle2'])
#muscle_agg.loc[muscle_agg['muscle1'] == '', 'muscle1'] = muscle_agg[muscle_agg['muscle1'] == '']['muscle2']

pie = px.pie(   
    muscle_agg, 
    values='count', 
    names='muscle1', 
    color_discrete_sequence=px.colors.sequential.Sunset_r, 
).update_layout(
    title = "Procentowy udział trenowanych mięśni"
).update_traces(
    hovertemplate = "<b>%{label}</b><br>" + "Liczba treningów tej partii: %{value}" + "<extra></extra>"
)
    
with col22:
    st.plotly_chart(pie, theme="streamlit", use_container_width=True)

###############################################################################################
# Third row - push ups, pull ups and dips over time
###############################################################################################
col31, col32 = st.columns(2)

pull_up_variations_all = exercises[exercises['exercise'].str.contains('podciąganie', na=False)]['exercise'].to_list()
fig_pull = px.bar(
    cal_agg[cal_agg['exercise'].isin(pull_up_variations_all)],
    x = 'date', 
    y = "reps_sum",
    color='exercise', 
    color_discrete_sequence=px.colors.sequential.Sunset_r, 
    custom_data=['exercise',granulation_hover]
).update_layout(
    plot_bgcolor='white',
    showlegend=False,
    xaxis_title = granulation_name,
    yaxis_title= "Liczba powtórzeń" ,
    title = "Wykonane powtórzenia podciągnięć",
).update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
).update_traces(
    hovertemplate = "<b>%{customdata[0]}</b><br>" + "%{customdata[1]}<br>" + "Liczba powtórzeń: %{y}" + "<extra></extra>"
)

with col31:
    st.plotly_chart(fig_pull, theme="streamlit", use_container_width=True)

fig_push = px.bar(
    cal_agg[(cal_agg['exercise'].isin(push_up_variations)) | (cal_agg['exercise'].isin(dip_variations))],
    x = 'date', 
    y = "reps_sum",
    color='exercise', 
    color_discrete_sequence=px.colors.sequential.Sunset_r, 
    custom_data=['exercise',granulation_hover]
).update_layout(
    plot_bgcolor='white',
    showlegend=False,
    xaxis_title = granulation_name,
    yaxis_title= "Liczba powtórzeń" ,
    title = "Wykonane powtórzenia pompek i dipów",
).update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
).update_traces(
    hovertemplate = "<b>%{customdata[0]}</b><br>" + "%{customdata[1]}<br>" + "Liczba powtórzeń: %{y}" + "<extra></extra>"
)

with col32:
    st.plotly_chart(fig_push, theme="streamlit", use_container_width=True)
