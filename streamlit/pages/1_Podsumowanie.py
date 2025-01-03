# plots with all sports summed up together

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import datetime
from data_processing import filter_by_period, hour_str, create_pallete
import plotly.express as px


st.set_page_config(
    page_title="Podsumowanie", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Podsumowanie wszystkich treningów")

alt.themes.enable("dark")

if "workouts" not in st.session_state:
    st.session_state["workouts"] = pd.read_csv("files/workouts.csv", sep='|')

if "calendar" not in st.session_state:
    st.session_state["calendar"] = pd.read_csv("files/calendar.csv", sep='|')

if "sports" not in st.session_state:
    st.session_state["sports"] = pd.read_csv("files/sports.csv", sep='|')

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
    'date',
    st.session_state["calendar"]['date'].min(),
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
        selected_month_start = st.selectbox('Miesiąc początkowy', month_list_start['month_name_pl'].tolist(), index=datetime.datetime.today().month)
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


    # prepare calendar for drawing plots
    calendar = filter_by_period(st.session_state["calendar"], 'date', st.session_state["min_date"], st.session_state["max_date"])
    calendar = calendar[~calendar['sport'].isna()]
    calendar = calendar[calendar['sport'] != '']
    

    # select sport categories (sport alone can be a cetegory or multiple sports can be concatenated)
    calndar_type = st.radio(
        'Rodzaje sportów',
        ['Wszystkie', 'Kategorie', 'Bieganie i sporty siłowe', 'Własny wybór']
    )
    # default options
    calendar_filtered = calendar    # calendar filetered by sports chosen in categories
    category = 'sport'              # decides if sports should be grouped by sport name or category name
    pallete = create_pallete(st.session_state["sports"], 'sport', 'sport_color')            # pallete choice for given category

    # set options according to selected values
    if calndar_type == 'Wszystkie':
        calendar_filtered = calendar
        category = 'sport'
        pallete = create_pallete(st.session_state["sports"], 'sport', 'sport_color')

    elif calndar_type == 'Kategorie':
        calendar_filtered = calendar
        category = 'category'
        pallete = create_pallete(st.session_state["sports"], 'category', 'sport_category_color') 

    elif calndar_type == 'Bieganie i sporty siłowe':
        calendar_filtered = calendar[calendar['sport'].isin(['bieganie', 'siłownia', 'kalistenika'])]
        category = 'sport'
        pallete = create_pallete(st.session_state["sports"], 'sport', 'run_work')

    elif calndar_type == 'Własny wybór':
        with st.sidebar:
            multiselect = st.multiselect(
                label="Wybierz sporty",
                options=calendar['sport'].unique()
            )
        calendar_filtered = calendar[calendar['sport'].isin(multiselect)]
        category = 'sport'
        pallete = create_pallete(st.session_state["sports"], 'sport', 'sport_color')

###############################################################################################
# prepare data for the plots
###############################################################################################
calendar_filtered['sport_count'] = calendar_filtered['sport']                       # prepare for aggregation
plot_data = calendar_filtered.groupby([category] + granulation_agg).agg({           # aggregate sport by chosen category in the chosen granulation
    'sport_count' : 'count',
    'total_seconds' : 'sum'
}).reset_index()
plot_data.rename(columns = {new_date_name : 'date'}, inplace=True)                  # fix columns names to always have 'date' present
plot_data['hours'] = np.round(plot_data['total_seconds'] / 3600, 2)                 # add info about time as float
plot_data['hours_str'] = plot_data['total_seconds'].apply(lambda x : hour_str(x))   # add info about time as string in format 00:00:00

if granulation_name == 'Tydzień':                                                   # add column with dates of start and end of the week for hovers
    plot_data['week_start_end'] = plot_data['date'].astype(str) + ' - ' + plot_data['week_end_date'].astype(str)

plot_data_pie_time = calendar_filtered.groupby(category).agg({           # aggregate sport by chosen category in the chosen granulation
    'sport_count' : 'count',
    'total_seconds' : 'sum'
}).reset_index()
plot_data_pie_time['hours'] = np.round(plot_data_pie_time['total_seconds'] / 3600, 2)                 # add info about time as float
plot_data_pie_time['hours_str'] = plot_data_pie_time['total_seconds'].apply(lambda x : hour_str(x))   # add info about time as string in format 00:00:00


###############################################################################################
# plots - fist row
###############################################################################################
col11, col12, col13 = st.columns([1,2,2])

with col11:
    metric_data = plot_data['sport_count'].sum()
    st.metric(label="Łączna liczba treningów", value=int(metric_data))

with col12:
    training_time = plot_data['total_seconds'].sum()
    h, m,s =  int(training_time // 3600), int((training_time % 3600) // 60), int(training_time % 60)
    st.metric(label="Łączny czas treningów", value=f"{h} godzin {m} minut {s} sekund")

with col13:
    if metric_data == 0:
        avg_time = 0
    else:
        avg_time = training_time / metric_data
    h_avg, m_avg, s_avg =  int(avg_time // 3600), int((avg_time % 3600) // 60), int(avg_time % 60)
    st.metric(label="Średni czas treningu", value=f"{h_avg} godzin {m_avg} minut {s_avg} sekund")


###############################################################################################
# plots - second row, number of workouts
###############################################################################################
col21, col22 = st.columns(2)

with col21:
    fig = px.bar(
        plot_data,
        x = 'date', 
        y = "sport_count",
        color=category, 
        color_discrete_map=pallete, 
        custom_data=[category,granulation_hover], 
    ).update_layout(
        plot_bgcolor='white',
        showlegend=False,
        xaxis_title = granulation_name,
        yaxis_title= "Liczba treningów" ,
        title = "Liczba treningów w przedziale czasowym",
    ).update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y"
    ).update_traces(
        hovertemplate = "<b>%{customdata[0]}</b><br>" + "%{customdata[1]}<br>" + "Liczba treningów: %{y}" + "<extra></extra>",
    )
    
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

with col22:
    pie = px.pie(
        plot_data, 
        values='sport_count', 
        names=category, 
        color=category,  
        color_discrete_map=pallete,
        custom_data=[category, 'sport_count'], 
    ).update_layout(
        title= "Procentowy udział sportów w treningach"
    ).update_traces(
        hovertemplate = "<b>%{label}</b><br>" + "Liczba treningów: %{value}" + "<extra></extra>"
    )
    
    st.plotly_chart(pie, theme="streamlit", use_container_width=True)


###############################################################################################
# plots - third row, time of workouts
###############################################################################################
col31, col32 = st.columns(2)

with col31:
    fig_count = px.bar(
        plot_data,
        x = 'date', 
        y = "hours",
        color=category, 
        color_discrete_map=pallete, 
        custom_data=[category, granulation_hover, 'hours_str', ],
    ).update_layout(
        plot_bgcolor='white',
        showlegend=False,
        xaxis_title = granulation_name,
        yaxis_title= "Czas treningów" ,
        title = "Czas treningów w przedziale czasowym",
        #margin=dict(l=20, r=30, t=10, b=20),
    ).update_xaxes(
        dtick="M1",
        tickformat="%b\n%Y"
    ).update_traces(
        hovertemplate = "<b>%{customdata[0]}</b><br>" + "%{customdata[1]}<br>" + "Czas treningów: %{customdata[2]}" + "<extra></extra>"
    )
    
    st.plotly_chart(fig_count, theme="streamlit", use_container_width=True)

with col32:
    pie_time = px.pie(
        plot_data_pie_time, 
        values='hours', 
        names=category, 
        color=category,  
        color_discrete_map=pallete,
        custom_data=['hours_str']
    ).update_layout(
        title = "Procentowy udział czasu uprawaniu sportów",
    ).update_traces(
        hovertemplate = "<b>%{label}</b><br>" + "Czas treningów: %{customdata[0]}"+ "<extra></extra>"
    )

    st.plotly_chart(pie_time, theme="streamlit", use_container_width=True)

    