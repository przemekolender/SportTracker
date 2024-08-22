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
gym_all = workouts[workouts['sport'] == 'siłownia']

gym_all = gym_all.merge(
    right = calendar,
    on = 'date',
    how = 'right'
)
gym_all['reps'] = gym_all['reps'].fillna(0)
gym_all['weight'] = gym_all['weight'].fillna(0)
gym_all['weights_lifted'] = gym_all['weights_lifted'].fillna(0)

gym_all.loc[:,'muscle1'] = gym_all['muscle1'].fillna('')
gym_all.loc[:,'muscle2'] = gym_all['muscle2'].fillna('')

gym_agg = gym_all.groupby([granulation_agg]) \
    .agg({
        'reps':'sum',
        'weight':'sum',
        'weights_lifted':'sum'
    }) \
    .reset_index()

gym_agg = gym_agg.merge(
    right = dates,
    on = granulation_agg,
    how = 'right'
)

gym_agg_set = gym_all.groupby(['exercise', 'sets', 'reps', 'weight']).size().reset_index()
gym_agg_set.columns = ['exercise', 'sets', 'reps', 'weight', 'times']

###############################################################################################
# first row - metrics
###############################################################################################
col11, col12 = st.columns(2)

with col11:
    reps = int(gym_all['reps'].sum())
    st.metric(label="Wykonane powtórzenia", value=format(reps, ',').replace(',', ' '))

with col12:
    weight = int(gym_all['weights_lifted'].sum())
    st.metric(label="Podniesiony ciężar", value=f"{format(weight, ',').replace(',', ' ')} kg")

###############################################################################################
# second row - favourite exercises and muscles
###############################################################################################
col21, col22 = st.columns(2)

gym_ex_agg_temp = gym_all.groupby(['exercise', 'date', 'muscle1', 'muscle2']) \
    .agg({
        'reps':'sum',
        'weight':'sum',
        'weights_lifted':'sum'
    }) \
    .reset_index()

gym_ex_agg_temp['exercise_count'] = gym_ex_agg_temp['exercise']

gym_ex_agg = gym_ex_agg_temp.groupby(['exercise']) \
    .agg({
        'exercise_count' : 'count',
        'reps':'sum',
        'weight':'sum',
        'weights_lifted':'sum'
    }) \
    .reset_index() \
    .sort_values('exercise_count', ascending = True) \
    .tail(10)


fig_fav = px.bar(
    gym_ex_agg,
    x = "exercise_count", 
    y = "exercise",
    title = "Najczęśniej wykonywane ćwiczenia",
    orientation='h',
    color_discrete_sequence=px.colors.sequential.Peach_r,
    custom_data=['exercise', 'exercise_count']
).update_layout(
    plot_bgcolor='white',
    xaxis_title = "Liczba wystąpień",
    yaxis_title= "Ćwiczenie" ,
).update_traces(
    hovertemplate = "<b>%{customdata[0]}</b><br>" + "Liczba wystąpieć ćwiczenia: %{customdata[1]}<br>" + "<extra></extra>"
)

with col21:
    st.plotly_chart(fig_fav, theme="streamlit", use_container_width=True)

gym_ex_agg_temp['muscle1_count'] = gym_ex_agg_temp['muscle1']
gym_ex_agg_temp['muscle2_count'] = gym_ex_agg_temp['muscle2']
muscle1_agg = gym_ex_agg_temp.groupby('muscle1').agg({'muscle1_count': 'count'}).reset_index()
muscle2_agg = gym_ex_agg_temp[gym_ex_agg_temp['muscle2'] != ''].groupby('muscle2').agg({'muscle2_count': 'count'}).reset_index()
muscle_agg = pd.merge(
    left=muscle1_agg,
    right=muscle2_agg,
    left_on='muscle1',
    right_on='muscle2',
    how = 'outer'
)
muscle_agg['count'] = muscle_agg['muscle1_count'].fillna(0) * 2 + muscle_agg['muscle2_count'].fillna(0)
muscle_agg.loc[:, 'muscle1'] = muscle_agg['muscle1'].fillna(muscle_agg['muscle2'])
pie = px.pie(   
    muscle_agg, 
    values='count', 
    names='muscle1', 
    title="Udział trenowanych partii",
    color_discrete_sequence=px.colors.sequential.Peach_r
).update_traces(
    hovertemplate = "<b>%{label}</b><br>" + "Liczba treningów tej partii: %{value}" + "<extra></extra>"
)
    
with col22:
    st.plotly_chart(pie, theme="streamlit", use_container_width=True)





###############################################################################################
# third row - reps and weight over time
###############################################################################################
col31, col32 = st.columns(2)

fig_reps = px.area(
    gym_agg, 
    x = 'date', 
    y = 'reps', 
    line_shape='spline', 
    markers=True,
    color_discrete_sequence=px.colors.sequential.Peach_r,
    custom_data=[granulation_hover]
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*gym_agg['reps'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Wykonane powtórzenia" ,
    title = "Liczba powtórzeń wykonan w danym okresie"
).update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
).update_traces(
    hovertemplate = "%{customdata[0]}<br>" + "Wykonane powtórzenia: %{y}<br>" + "<extra></extra>"
)

with col31:
    st.plotly_chart(fig_reps, theme="streamlit", use_container_width=True)


fig_weight = px.area(
    gym_agg, 
    x = 'date', 
    y = 'weights_lifted', 
    line_shape='spline', 
    markers=True,
    color_discrete_sequence=px.colors.sequential.Peach_r,
    custom_data=[granulation_hover]
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*gym_agg['weights_lifted'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Podniesiony ciężar" ,
    title = "Liczba podniesionych kilogramów w danym okresie"
).update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
).update_traces(
    hovertemplate = "%{customdata[0]}<br>" + "Podniesionyy ciężar: %{y} kg<br>" + "<extra></extra>"
)

with col32:
    st.plotly_chart(fig_weight, theme="streamlit", use_container_width=True)


###############################################################################################
# fourth row - bench and ohp scatters
###############################################################################################
col41, col42 = st.columns(2)

bench = gym_agg_set[gym_agg_set['exercise'] == 'wyciskanie na ławce płaskiej']
fig_bench = px.scatter(
    bench, 
    x = 'reps', 
    y = 'weight',
    size= 'times',
    color_discrete_sequence=px.colors.sequential.Peach_r,
    custom_data=['times']
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*bench['weight'].max()],
    xaxis_title = "Liczba powtórzeń",
    yaxis_title= "Waga" ,
    title = "Wyciskanie",
).update_traces(
    hovertemplate = "Liczba powtórzeń: %{x}<br>" + "Ciężar: %{y}<br>" + "Liczba serii: %{customdata[0]}<br>" + "<extra></extra>"
)

with col41:
    st.plotly_chart(fig_bench, theme="streamlit", use_container_width=True)


ohp = gym_agg_set[(gym_agg_set['exercise'] == 'ohp') | (gym_agg_set['exercise'] == 'martwy + ohp')]
fig_ohp = px.scatter(
    ohp, 
    x = 'reps', 
    y = 'weight',
    size= 'times',
    color_discrete_sequence=px.colors.sequential.Peach_r,
    custom_data=['times']
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*ohp['weight'].max()],
    xaxis_title = "Liczba powtórzeń",
    yaxis_title= "Waga" ,
    title = "Ohp",
).update_traces(
    hovertemplate = "Liczba powtórzeń: %{x}<br>" + "Ciężar: %{y}<br>" + "Liczba serii: %{customdata[0]}<br>" + "<extra></extra>"
)

with col42:
    st.plotly_chart(fig_ohp, theme="streamlit", use_container_width=True)

###############################################################################################
# fifth row - deadlist and squat scatters
###############################################################################################
col51, col52 = st.columns(2)

squat = gym_agg_set[gym_agg_set['exercise'] == 'przysiady']
fig_squat = px.scatter(
    squat, 
    x = 'reps', 
    y = 'weight',
    size= 'times',
    color_discrete_sequence=px.colors.sequential.Peach_r,
    custom_data=['times']
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*squat['weight'].max()],
    xaxis_title = "Liczba powtórzeń",
    yaxis_title= "Waga" ,
    title = "Przysiady",
).update_traces(
    hovertemplate = "Liczba powtórzeń: %{x}<br>" + "Ciężar: %{y}<br>" + "Liczba serii: %{customdata[0]}<br>" + "<extra></extra>"
)

with col51:
    st.plotly_chart(fig_squat, theme="streamlit", use_container_width=True)


deadlift = gym_agg_set[(gym_agg_set['exercise'] == 'martwy ciąg') | (gym_agg_set['exercise'] == 'martwy + ohp')]
fig_deadlift = px.scatter(
    deadlift, 
    x = 'reps', 
    y = 'weight',
    size= 'times',
    color_discrete_sequence=px.colors.sequential.Peach_r,
    custom_data=['times']
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*deadlift['weight'].max()],
    xaxis_title = "Liczba powtórzeń",
    yaxis_title= "Waga" ,
    title = "Martwy ciąg",
).update_traces(
    hovertemplate = "Liczba powtórzeń: %{x}<br>" + "Ciężar: %{y}<br>" + "Liczba serii: %{customdata[0]}<br>" + "<extra></extra>"
)

with col52:
    st.plotly_chart(fig_deadlift, theme="streamlit", use_container_width=True)
