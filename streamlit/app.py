import sys
sys.path.append("data")
import os
import streamlit as st
import pandas as pd
import altair as alt
#import plotly.express as px
from matplotlib.colors import LinearSegmentedColormap
import datetime
import plotly.express as px
import plotly.graph_objects as go

from data_processing import best_weight, most_reps, best_run, filter_by_period, create_pallete


st.set_page_config(
    page_title="SportTracker",
    page_icon="🏋️‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.theme.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|')

if "calendar" not in st.session_state:
    st.session_state["calendar"] = pd.read_csv("files/calendar.csv", sep='|')

if "sports" not in st.session_state:
    st.session_state["sports"] = pd.read_csv("files/sports.csv", sep='|')

if "max_date" not in st.session_state:
    st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')


###############################################################################################
# draw calendar
###############################################################################################

st.markdown("# Kalendarz treningów")

with st.sidebar:
    calndar_type = st.radio(
        'Rodzaje sportów',
        ['Ogólne aktywności', 'Wszystkie', 'Kategorie', 'Bieganie i sporty siłowe', 'Własny wybór']
    )


c = filter_by_period(st.session_state["calendar"], 'date', st.session_state["calendar"]['date'].min(), st.session_state["max_date"])
c.loc[:, 'sport'] = c['sport'].fillna('-')
c.loc[:, 'category'] = c['category'].fillna('-')

# group by to concatenate 2 or more sports sport in 1 day
c = c.groupby(['index', 'date', 'week_start_date', 'week_day', 'day_of_week_name_pl'], as_index = False)\
    .agg({'sport': ', '.join,
          'category': ', '.join})\
    .reset_index(drop = True)

# function helps to find color for sports and categories
def find_sport(sports, pallete):
    sports_arr = sports.split(', ')
    for sport in sports_arr:
        if pallete[sport] != 'lightgray':
            return pallete[sport]
    return 'lightgray'

if calndar_type == 'Wszystkie':
    color = c['sport'].apply(lambda x : find_sport(x, create_pallete(st.session_state["sports"], 'sport', 'sport_color')))

elif calndar_type == 'Kategorie':
    color = c['category'].apply(lambda x : find_sport(x, create_pallete(st.session_state["sports"], 'category', 'sport_category_color')))

elif calndar_type == 'Bieganie i sporty siłowe':
    color =  c['sport'].apply(lambda x : find_sport(x, create_pallete(st.session_state["sports"], 'sport', 'run_work')))

elif calndar_type == 'Ogólne aktywności':
    color = c['sport'].apply(lambda x : find_sport(x, create_pallete(st.session_state["sports"], 'sport', 'event_color')))

elif calndar_type == 'Własny wybór':
    with st.sidebar:
        multiselect = st.multiselect(
            label="Wybierz sporty",
            options=c['sport'].unique()
        )

    # finding colors to manually selected sports
    color = []
    for sport_row in c['sport']:
        flag = 0
        sports = str(sport_row).split(', ')
        for sport in sports:
            if sport in multiselect:
                color.append('green')
                flag = 1
                break
        if flag == 0:
            color.append('lightgray')

# createing information about sports in given day
info = []
for i in range(len(color)):
    if color[i] == 'lightgray':
        info.append(None)
    else:
        info.append(str(c.loc[i, 'date']) + ': ' + str(c.loc[i, 'sport']))
c['info'] = info


###############################################################################################
# draw calendar heatmap
###############################################################################################
fig = go.Figure(go.Scatter(
    x=c['week_start_date'], 
    y=c['day_of_week_name_pl'], 
    text=c['info'],
    hoverinfo = 'text',
    mode='markers', 
    marker = dict(size=13, symbol='square', color = color)
))
fig.update_yaxes(categoryorder='array', categoryarray= ['Niedziela', 'Sobota', 'Piątek', 'Czwartek', 'Środa', 'Wtorek', 'Poniedziałek'])
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis_title = None,
    yaxis_title=None   
)
fig.update_xaxes(
    ticklabelmode="period",
    dtick="M1",
    tickformat="%b\n%Y"
)
fig.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label="Ostatni miesiąc",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="Ostatnie 6 miesięcy",
                     step="month",
                     stepmode="backward"),
                dict(count=1,
                     label="Ten rok",
                     step="year",
                     stepmode="todate"),
                dict(count=1,
                     label="Ostatni rok",
                     step="year",
                     stepmode="backward"),
                dict(step="all",
                     label="Wszystkie aktywności")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

st.plotly_chart(fig, width='stretch')



###############################################################################################
# draw metrics
###############################################################################################
workouts = st.session_state["workouts"]

st.markdown("## Rekordy w kalistenice")
col11, col12, col13, col14 = st.columns(4)

with col11:
    max_reps = most_reps(workouts, 'podciąganie nachwytem')
    st.metric(label="Najwięcej podciągnięć nachwytem", value=max_reps)
   
with col12:
    max_reps = most_reps(workouts, 'dipy')
    st.metric(label="Najwięcej dipów", value=max_reps)
   
with col13:
    max_reps = most_reps(workouts, 'pompki')
    st.metric(label="Najwięcej pompek", value=max_reps)

with col14:
    max_reps = most_reps(workouts, 'muscle up')
    st.metric(label="Najwięcej muscleupów", value=max_reps)


st.markdown('## Rekory na siłowni')
col21, col22, col23, col24 = st.columns(4)

with col21:
    max_weight, max_weight_reps = best_weight(workouts, 'wyciskanie na ławce płaskiej')
    st.metric(label="Wyciskanie", value=max_weight, delta=max_weight_reps, delta_color='off')

with col22:
    max_weight, max_weight_reps = best_weight(workouts, 'przysiady')
    st.metric(label="Przysiad", value=max_weight, delta=max_weight_reps, delta_color='off')

with col23:
    max_weight, max_weight_reps = best_weight(workouts, 'martwy ciąg')
    st.metric(label="Martwy ciąg", value=max_weight, delta=max_weight_reps, delta_color='off')

with col24:
    max_weight, max_weight_reps = best_weight(workouts, 'ohp')
    st.metric(label="OHP", value=max_weight, delta=max_weight_reps, delta_color='off')


st.markdown('## Rekory w bieganiu')
col31, col32, col33, col34 = st.columns(4)

with col31:
    time, pace = best_run(workouts, 5)
    st.metric(label="5km", value=time, delta=pace, delta_color='off')

with col32:
    time, pace = best_run(workouts, 10)
    st.metric(label="10km", value=time, delta=pace, delta_color='off')

with col33:
    time, pace = best_run(workouts, 21.1)
    st.metric(label="Półmaraton", value=time, delta=pace, delta_color='off')

with col34:
    time, pace = best_run(workouts, 42.2)
    st.metric(label="Maraton", value=time, delta=pace, delta_color='off')

