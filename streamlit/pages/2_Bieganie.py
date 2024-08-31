# running

import streamlit as st
import altair as alt
import datetime
import pandas as pd
from data_processing import filter_by_period, transpose_runs, hour_str
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
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|')
    st.session_state["workouts"]["date"] = pd.to_datetime(st.session_state["workouts"]["date"], format='%Y-%m-%d')

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
    max_day = st.session_state["calendar"][st.session_state["calendar"]["month_name_pl"] ==  selected_month_start]['day_num'].unique()[0]

    st.session_state["min_date"] = f"{selected_year_start}-{selected_month_start_num}-{min_day}"
    st.session_state["max_date"] = f"{selected_year_end}-{selected_month_end_num}-{max_day}"


    # select granulation
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


workouts = filter_by_period(
    st.session_state["workouts"],
    'date',
    st.session_state['min_date'],
    st.session_state['max_date']
)
calendar = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])
runs_all = workouts[workouts['sport'] == 'bieganie']
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

runs = runs_all.groupby([granulation_agg]) \
    .agg({
        'distance_km':'sum',
        'run_hours':'sum',
        'run_minutes':'sum',
        'run_seconds':'sum',
        'run_total_seconds':'sum'
    }) \
    .reset_index()

runs['hour_str'] = runs['run_total_seconds'].apply(lambda x : hour_str(int(x)))
runs = runs.merge(
    right = dates,
    on = granulation_agg,
    how = 'right'
)


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
    x = 'date', 
    y = 'distance_km', 
    line_shape='spline', 
    markers=True,
    custom_data=[granulation_hover]
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*runs['distance_km'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Przebiegnięty dystans" ,
    title = "Przebiegnięty dystans w danym okresie"
).update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
).update_traces(
    hovertemplate = "%{customdata[0]}<br>" + "Dystans: %{y} km<br>" + "<extra></extra>"
)

runs['h'] = runs['run_total_seconds'] / 3600
fig_time = px.area(
    runs, 
    x = 'date', 
    y = 'h', 
    line_shape='spline', 
    markers=True,
    custom_data=[granulation_hover, 'hour_str']
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*runs['h'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Czas biegania" ,
    title = "Czas biegania w danym okresie"
).update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
).update_traces(
    hovertemplate = "%{customdata[0]}<br>" + "Czas biegania: %{customdata[1]}<br>" + "<extra></extra>"
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
runs_t['hour_str'] = runs_t['run_total_seconds'].apply(lambda x : hour_str(int(x)))
fig_scatter = px.scatter(
    runs_t, 
    x = 'h', 
    y = 'distance_km',
    trendline='lowess',
    trendline_color_override='lightblue',
    custom_data=['hour_str']
).add_trace(
    go.Scatter(
        x=[0, 1, 2, 3],
        y=[0, 12, 24, 36],
        mode="lines",
        line=go.scatter.Line(color="palevioletred", dash='dash'),
        showlegend=False
    )
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*runs_all['distance_km'].max()],
    xaxis_title = "Czas biegania",
    yaxis_title= "Dystans" ,
    title = "Zależność przebiegniętego dystansu od czas"
).update_traces(
    hovertemplate = "Dystans: %{y} km<br>" + "Czas biegania: %{customdata[0]}<br>" + "<extra></extra>"
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