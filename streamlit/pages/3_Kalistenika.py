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
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|')
    #st.session_state["workouts"]["date"] = pd.to_datetime(st.session_state["workouts"]["date"], format='%Y-%m-%d')

if "calendar" not in st.session_state:
    st.session_state["calendar"] = pd.read_csv("files/calendar.csv", sep='|')
    st.session_state["calendar"]["date"] = pd.to_datetime(st.session_state["calendar"]["date"], format='%Y-%m-%d')

if "min_date" not in st.session_state:
    st.session_state["min_date"] = st.session_state["calendar"]['date'].min()

if "max_date" not in st.session_state:
    st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')


###############################################################################################
# sidebar options
###############################################################################################

# always use dates no greater than today
st.session_state["calendar"] = filter_by_period(
    st.session_state["calendar"],
    'date', st.session_state["calendar"]['date'].min(),
    datetime.datetime.today().strftime(format='%Y-%m-%d')
)

with st.sidebar:   

    # select start year and month
    col_year_start, col_month_start = st.columns(2)
    with col_year_start:
        year_list_start = st.session_state["calendar"]['year'].unique().tolist()
        selected_year_start = st.selectbox('Rok początkowy', year_list_start, index=len(year_list_start)-1)
  
    with col_month_start:
        month_list_start = st.session_state["calendar"].loc[
            st.session_state["calendar"]['year'] == selected_year_start, ['month','month_name_pl']
        ].groupby(['month','month_name_pl']).all().reset_index()
        selected_month_start = st.selectbox('Miesiąc początkowy', month_list_start['month_name_pl'].tolist(), index=0)
        selected_month_start_int = month_list_start.loc[month_list_start['month_name_pl'] == selected_month_start, 'month'].tolist()[0]


    # select end year and month
    col_year_end, col_month_end = st.columns(2)
    with col_year_end:
        year_list_end = st.session_state["calendar"].loc[st.session_state["calendar"]['year'] >= selected_year_start, 'year'].unique().tolist()
        selected_year_end = st.selectbox('Rok końcowy', year_list_end, index=len(year_list_end)-1)

    with col_month_end:
        if selected_year_end == selected_year_start:
            month_list_end = st.session_state["calendar"].loc[
                (st.session_state["calendar"]['year'] == selected_year_end) & 
                (st.session_state["calendar"]['month'] >= selected_month_start_int)
                , 'month_name_pl'].unique().tolist()
        else:
            month_list_end = st.session_state["calendar"].loc[(st.session_state["calendar"]['year'] == selected_year_end), 'month_name_pl'].unique().tolist()
        selected_month_end = st.selectbox('Miesiąc końcowy', month_list_end, index=len(month_list_end)-1)


    # set min_date and max_date according to selected values
    selected_month_start_num = st.session_state["calendar"][st.session_state["calendar"]["month_name_pl"] ==  selected_month_start]['month_str'].unique()[0]
    selected_month_end_num = st.session_state["calendar"][st.session_state["calendar"]["month_name_pl"] ==  selected_month_end]['month_str'].unique()[0]
    min_day = '01'
    max_day = st.session_state["calendar"][st.session_state["calendar"]["month_name_pl"] ==  selected_month_end]['day_num'].unique()[0]

    st.session_state["min_date"] = f"{selected_year_start}-{selected_month_start_num}-{min_day}"
    st.session_state["max_date"] = f"{selected_year_end}-{selected_month_end_num}-{max_day}"


    # select granulation
    granulation_name = st.radio(
        label="Wybierz granulację",
        options=['Miesiąc', 'Tydzień', 'Dzień']
    )

    # prepare filed names for grouping by date
    if granulation_name == 'Dzień':
        granulation_agg = ['date'] 
        new_date_name = 'date'
        granulation_hover = 'date'
    elif granulation_name == 'Tydzień':
        granulation_agg = ['year','week','year_week', 'week_start_date', 'week_end_date']
        new_date_name = 'week_start_date'
        granulation_hover = 'week_start_end'
    else:
        granulation_agg = ['year','month','month_str','month_name_en','month_name_pl','year_month', 'fake_month_date']
        new_date_name = 'fake_month_date'
        granulation_hover = 'month_name_pl'


###############################################################################################
# preparing data
###############################################################################################
workouts = filter_by_period(
    st.session_state["workouts"],
    'date',
    st.session_state['min_date'],
    st.session_state['max_date']
)
calendar = filter_by_period(
    st.session_state["calendar"],
    'date', 
    st.session_state["min_date"], 
    st.session_state["max_date"]
)

# clear calendar if more than one activity on a day
calendar = calendar.drop(['Unnamed: 0', 'sport', 'time', 'info', 'hours', 'minutes', 'seconds', 'total_seconds', 'category', 'isdistance'], axis = 1)
calendar = calendar.groupby(calendar.columns.to_list()).size().reset_index()

cal_all = workouts[workouts['sport'] == 'kalistenika']
cal_all.loc[:, 'muscle1'] = cal_all['muscle1'].fillna('')
cal_all.loc[:, 'muscle2'] = cal_all['muscle2'].fillna('')

# grouping splitted rows of 1 exercise to get real number of appearances
cal_all = cal_all.groupby(['exercise', 'date', 'muscle1', 'muscle2']) \
    .agg({
        'reps_sum':'sum'
    }).reset_index()

# merge with calendar to have date info
cal_all = cal_all.merge(
    right = calendar,
    on = 'date',
    how = 'right'
)

# grouping by granutlation period
cal_all['exercise_count'] = cal_all['exercise']
cal_agg = cal_all.groupby(['exercise'] + granulation_agg + ['muscle1', 'muscle2']) \
    .agg({
        'exercise_count' : 'count',
        'reps_sum':'sum'
    }).reset_index()
cal_agg.rename(columns = {new_date_name : 'date'}, inplace=True)                    # fix columns names to always have 'date' present
if granulation_name == 'Tydzień':                                                   # add column with dates of start and end of the week for hovers
    cal_agg['week_start_end'] = cal_agg['date'].astype(str) + ' - ' + cal_agg['week_end_date'].astype(str)

# find all exercises
exercises = pd.DataFrame(st.session_state["workouts"]['exercise'].unique(), columns=['exercise'])

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

# prepare data for pie chart with trained muscles
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

