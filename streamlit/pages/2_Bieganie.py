# running

import streamlit as st
import altair as alt
import datetime
import pandas as pd
from data_processing import filter_by_period, transpose_runs, hour_str, create_pallete, run_hist, int_to_str
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Bieganie", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Bieganie")

alt.theme.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|')
    st.session_state["workouts"]["date"] = pd.to_datetime(st.session_state["workouts"]["date"], format='%Y-%m-%d')

if "calendar" not in st.session_state:
    st.session_state["calendar"] = pd.read_csv("files/calendar.csv", sep='|')
    st.session_state["calendar"]["date"] = pd.to_datetime(st.session_state["calendar"]["date"], format='%Y-%m-%d')

if "sports" not in st.session_state:
    st.session_state["sports"] = pd.read_csv("files/sports.csv", sep='|')

if "min_date" not in st.session_state:
    st.session_state["min_date"] = st.session_state["calendar"]['date'].min()

if "max_date" not in st.session_state:
    st.session_state["max_date"] = datetime.datetime.today().strftime(format='%Y-%m-%d')

if "month_index_run" in st.session_state:
    st.session_state["month_index_run"] = 0 
else:
    st.session_state["month_index_run"] = datetime.datetime.today().month


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
        selected_month_start = st.selectbox('Miesiąc początkowy', month_list_start['month_name_pl'].tolist(), index = st.session_state["month_index_run"])
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


    # choose sports
    sports = st.multiselect(
        options= st.session_state['sports'].loc[st.session_state['sports']['isdistance'] == 'tak', 'sport'].to_list(),
        default='bieganie',
        label='Wybierz sporty'
    )
    

workouts = filter_by_period(
    st.session_state["workouts"],
    'date',
    st.session_state['min_date'],
    st.session_state['max_date']
)
calendar = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])

# clear calendar if more than one activity on a day
calendar = calendar.drop(['Unnamed: 0', 'sport', 'time', 'info', 'hours', 'minutes', 'seconds', 'total_seconds', 'category', 'isdistance'], axis = 1)
calendar = calendar.groupby(calendar.columns.to_list()).size().reset_index()

runs_all = workouts[workouts['sport'].isin(sports)]
runs_all["date"] = pd.to_datetime(runs_all["date"], format='%Y-%m-%d')
calendar["date"] = pd.to_datetime(calendar["date"], format='%Y-%m-%d')
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

runs = runs_all.groupby(granulation_agg) \
    .agg({
        'distance_km':'sum',
        'run_hours':'sum',
        'run_minutes':'sum',
        'run_seconds':'sum',
        'run_total_seconds':'sum'
    }) \
    .reset_index()
runs.rename(columns = {new_date_name : 'date'}, inplace=True)                  # fix columns names to always have 'date' present
runs['hour_str'] = runs['run_total_seconds'].apply(lambda x : hour_str(int(x)))
runs['pace_seconds'] = (runs['run_total_seconds'] / runs['distance_km']).round(0).fillna(0)
runs['pace'] = (runs['pace_seconds'].astype(int) // 60).astype(str) + "'" + (runs['pace_seconds'].astype(int) % 60).apply(lambda x : int_to_str(int(x))).astype(str)
if granulation_name == 'Tydzień':                                                   # add column with dates of start and end of the week for hovers
    runs['week_start_end'] = runs['date'].astype(str) + ' - ' + runs['week_end_date'].astype(str)

runs_t = transpose_runs(runs_all)
runs_t['h'] = runs_t['run_total_seconds'] / 3600
runs_t['date_'] = runs_t['date'].astype(str).str[:11]

runs_t['pace_num'] = runs_t['pace'].apply(lambda x : float(str(x)[0]) + float(str(x)[-2:]) / 60)
runs_t['pace_seconds'] = runs_t['pace'].apply(lambda x : int(str(x).split("'")[0])*60 + int(str(x).split("'")[1]))

nbins = 17
runs_hist_dist = run_hist(nbins, runs_t, 'distance_km', 2, 1, 0.01)

runs_hist_pace = run_hist(nbins, runs_t, 'pace_seconds', 260, 5, 1)
runs_hist_pace['bin_min_s'] = runs_hist_pace['bin_min'].apply(lambda x : f"{x // 60}'{int_to_str(x % 60)}")
runs_hist_pace['bin_max_s'] = runs_hist_pace['bin_max'].apply(lambda x : f"{x // 60}'{int_to_str((x) % 60)}")
runs_hist_pace['interval2'] = runs_hist_pace['bin_min_s'] + ' - ' + runs_hist_pace['bin_max_s']
runs_hist_pace.loc[runs_hist_pace['nbin'] == nbins, 'interval2'] = runs_hist_pace['bin_min_s'] + ' - ∞' 

runs_hist_time = run_hist(nbins, runs_t, 'run_total_seconds', 600, 300, 1)
runs_hist_time['bin_min_t'] = runs_hist_time['bin_min'].apply(lambda x : f"{int_to_str(x // 3600)}:{int_to_str((x % 3600) // 60)}:{int_to_str(x % 60)}")
runs_hist_time['bin_max_t'] = runs_hist_time['bin_max'].apply(lambda x : f"{int_to_str((x) // 3600)}:{int_to_str(((x) % 3600) // 60)}:{int_to_str((x) % 60)}")
runs_hist_time['interval2'] = runs_hist_time['bin_min_t'].astype(str) + ' - ' + runs_hist_time['bin_max_t'].astype(str)
runs_hist_time.loc[runs_hist_time['nbin'] == nbins, 'interval2'] = runs_hist_time['bin_min_t'] + ' - ∞' 


###############################################################################################
# first row - metrics
###############################################################################################
col11, col12, col13 = st.columns([1, 2 ,1])
distnace = float(runs['distance_km'].sum()).__round__(2)
seconds_full = runs['run_total_seconds'].sum()

with col11:
    st.metric(label="Przebiegnięty dystans", value=f"{distnace} km")

with col12:
    h, m, s =  int(seconds_full // 3600), int((seconds_full % 3600) // 60), int(seconds_full % 60)
    st.metric(label="Czas biegania", value=f"{h} godzin {m} minut {s} sekund")

with col13:
    if distnace == 0:
        pace_m, pace_s = 0, 0
    else :
        pace_m, pace_s = int((seconds_full / distnace % 3600) // 60), int(round(seconds_full / distnace % 60, 0))
    st.metric(label="Średnie tempo", value=f"{int(pace_m)}'{int_to_str(pace_s)}")


###############################################################################################
# second row, distance
###############################################################################################
col21, col22 = st.columns(2)

fig_distance = px.area(
    runs, 
    x = 'date', 
    y = 'distance_km', 
    #line_group='sport',
    #color='sport',
    #color_discrete_map=distance_sports,
    line_shape='spline', 
    markers=True,
    custom_data=[granulation_hover]
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*runs['distance_km'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Przebiegnięty dystans [km]" ,
    title = "Przebiegnięty dystans w danym okresie",
    showlegend=False
).update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
).update_traces(
    hovertemplate = "%{customdata[0]}<br>" + "Dystans: %{y} km<br>" + "<extra></extra>"
)

fig_distance_hist = px.bar(
    runs_hist_dist,
    x = "interval", 
    y = "n",
).update_layout(
    plot_bgcolor='white',
    xaxis_title = "Przebiegnięty dystans [km]",
    yaxis_title = "Liczba wystąpień",
    title_x=0.3,
    title = "Histogram przebiegniętych dystansów"
).update_traces(
    hovertemplate = "Dystans: %{x} km<br>" + "Liczba wystąpień: %{y}<br>" + "<extra></extra>"
)


with col21:
    st.plotly_chart(fig_distance, theme="streamlit", use_container_width=True)

with col22:
    st.plotly_chart(fig_distance_hist, theme="streamlit", use_container_width=True)


###############################################################################################
# third row, pace
###############################################################################################
col31, col32 = st.columns(2)

fig_pace = px.area(
    runs, 
    x = 'date', 
    y = 'pace_seconds', 
    line_shape='spline', 
    markers=True,
    custom_data=[granulation_hover, 'pace']
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*runs['pace_seconds'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Średnie tempo biegu [s/km]" ,
    title = "Średnie tempo biegu w danym okresie",
    showlegend=False
).update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
).update_traces(
    hovertemplate = "%{customdata[0]}<br>" + "Tempo: %{customdata[1]} min/km<br>" + "<extra></extra>"
)



fig_hist = px.bar(
    runs_hist_pace,
    x = "interval2", 
    y = "n",
).update_layout(
    plot_bgcolor='white',
    xaxis_title = "Przedział tempa [min/km]",
    yaxis_title= "Liczba wystąpień" ,
    title_x=0.3,
    title = "Histogram tempa",
).update_traces(
    hovertemplate = "<b>%{x}</b><br>" + "Liczba wystąpień: %{y}<br>" + "<extra></extra>"
)

with col31:
    st.plotly_chart(fig_pace, theme="streamlit", use_container_width=True)

with col32:
    st.plotly_chart(fig_hist, theme="streamlit", use_container_width=True)


###############################################################################################
# fourth row, time
###############################################################################################
col41, col42 = st.columns(2)

runs['h'] = runs['run_total_seconds'] / 3600
fig_time = px.area(
    runs, 
    x = 'date', 
    y = 'h', 
    #color='sport',
    #color_discrete_map=distance_sports,
    line_shape='spline', 
    markers=True,
    custom_data=[granulation_hover, 'hour_str']
).update_layout(
    plot_bgcolor='white',
    yaxis_range=[0, 1.1*runs['h'].max()],
    xaxis_title = granulation_name,
    yaxis_title= "Czas biegania [h]" ,
    title = "Czas biegania w danym okresie",
    showlegend=False
).update_xaxes(
    dtick="M1",
    tickformat="%b\n%Y"
).update_traces(
    hovertemplate = "%{customdata[0]}<br>" + "Czas biegania: %{customdata[1]}<br>" + "<extra></extra>"
)

fig_time_hist = px.bar(
    runs_hist_time,
    x = "interval2", 
    y = "n",
).update_layout(
    plot_bgcolor='white',
    xaxis_title = "Czas biegania",
    yaxis_title = "Liczba wystąpień",
    title_x=0.3,
    title = "Histogram czasu biegania"
).update_traces(
    hovertemplate = "Czas biegu: %{x}<br>" + "Liczba wystąpień: %{y}<br>" + "<extra></extra>"
)

with col41:
    st.plotly_chart(fig_time, theme="streamlit", use_container_width=True)

with col42:
    st.plotly_chart(fig_time_hist, theme="streamlit", use_container_width=True)
    

###############################################################################################
# fifth row, distnace versus time
###############################################################################################

fig_scatter = px.scatter(
    runs_t, 
    x = 'h', 
    y = 'distance_km',
    trendline='lowess',
    trendline_color_override='lightblue',
    custom_data=['time', 'pace', 'date_'],
    color='sport',
    color_discrete_map= create_pallete(st.session_state["sports"], 'sport', 'sport_color')
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
    xaxis_title = "Czas biegania [h]",
    yaxis_title= "Dystans [km]" ,
    title = "Zależność przebiegniętego dystansu od czas",
    showlegend=False
).update_traces(
    hovertemplate = "Dystans: %{y} km<br>" + "Czas biegania: %{customdata[0]}<br>" + "Tempo: %{customdata[1]}<br>" + "%{customdata[2]}<br>" + "<extra></extra>"
)


st.plotly_chart(fig_scatter, theme="streamlit", use_container_width=True)
