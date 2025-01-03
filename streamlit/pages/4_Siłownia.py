# gym

import streamlit as st
import pandas as pd
import altair as alt
import datetime
from data_processing import filter_by_period
import plotly.express as px
 

st.set_page_config(
    page_title="Siłownia", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Treningi na siłowni")

alt.theme.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|')
    st.session_state["workouts"]["date"] = pd.to_datetime(st.session_state["workouts"]["date"], format='%Y-%m-%d')

if "calendar" not in st.session_state:
    st.session_state["calendar"] = pd.read_csv("files/calendar.csv", sep='|')
    st.session_state["calendar"]["date"] = pd.to_datetime(st.session_state["calendar"]["date"], format='%Y-%m-%d')

if "min_date" not in st.session_state:
    st.session_state["min_date"] = st.session_state["calendar"]['date'].min()

if "max_date" not in st.session_state:
    st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')

if "month_index" in st.session_state:
    st.session_state["month_index"] = 0 
else:
    st.session_state["month_index"] = datetime.datetime.today().month


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
        index_year_start = len(year_list_start)-2 if datetime.datetime.today().month < 12 else len(year_list_start)-1
        selected_year_start = st.selectbox('Rok początkowy', year_list_start, index=index_year_start)
  
    with col_month_start:
        month_list_start = st.session_state["calendar"].loc[
            st.session_state["calendar"]['year'] == selected_year_start, ['month','month_name_pl']
        ].groupby(['month','month_name_pl']).all().reset_index()
        selected_month_start = st.selectbox('Miesiąc początkowy', month_list_start['month_name_pl'].tolist(), index = st.session_state["month_index"])
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


gym_all = workouts[workouts['sport'] == 'siłownia']
gym_all.loc[:,'muscle1'] = gym_all['muscle1'].fillna('')
gym_all.loc[:,'muscle2'] = gym_all['muscle2'].fillna('')


# merge with calendar to have date info
gym_all["date"] = pd.to_datetime(gym_all["date"], format='%Y-%m-%d')
calendar["date"] = pd.to_datetime(calendar["date"], format='%Y-%m-%d')

gym_all = gym_all.merge(
    right = calendar,
    on = 'date',
    how = 'right'
)
gym_all['reps_sum'] = gym_all['reps_sum'].fillna(0)
gym_all['weight'] = gym_all['weight'].fillna(0)
gym_all['weights_lifted'] = gym_all['weights_lifted'].fillna(0)


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

# grouping splitted rows of 1 exercise to get real number of appearances
gym_ex_agg_temp = gym_all.groupby(['exercise', 'date', 'muscle1', 'muscle2']) \
    .agg({
        'reps_sum':'sum',
        'weight':'sum',
        'weights_lifted':'sum'
    }).reset_index()

# group exercises to sum all apperances, without periods
gym_ex_agg_temp['exercise_count'] = gym_ex_agg_temp['exercise']
gym_ex_agg = gym_ex_agg_temp.groupby(['exercise']) \
    .agg({
        'exercise_count' : 'count',
        'reps_sum':'sum',
        'weight':'sum',
        'weights_lifted':'sum'
    }).reset_index() \
    .sort_values('exercise_count', ascending = True) \
    .tail(10)

col21, col22 = st.columns(2)

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

# prepare data for pie chart with trained muscles
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

# group by time period to have number of reps and kg lifted over time
gym_agg = gym_all.groupby(granulation_agg) \
    .agg({
        'reps_sum':'sum',
        'weight':'sum',
        'weights_lifted':'sum'
    }) \
    .reset_index()
gym_agg.rename(columns = {new_date_name : 'date'}, inplace=True)                    # fix columns names to always have 'date' present
if granulation_name == 'Tydzień':                                                   # add column with dates of start and end of the week for hovers
    gym_agg['week_start_end'] = gym_agg['date'].astype(str) + ' - ' + gym_agg['week_end_date'].astype(str)


col31, col32 = st.columns(2)

fig_reps = px.area(
    gym_agg, 
    x = 'date', 
    y = 'reps_sum', 
    line_shape='spline', 
    markers=True,
    color_discrete_sequence=px.colors.sequential.Peach_r,
    custom_data=[granulation_hover]
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*gym_agg['reps_sum'].max()],
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

# group to find all identical sets
gym_agg_set = gym_all.groupby(['exercise', 'sets', 'reps', 'weight']).size().reset_index()
gym_agg_set.columns = ['exercise', 'sets', 'reps', 'weight', 'times']

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

