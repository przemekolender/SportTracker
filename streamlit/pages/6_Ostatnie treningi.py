# last gym, calistenics and running workouts preseted as a table

import streamlit as st
import pandas as pd
import altair as alt
import datetime
from data_processing import filter_by_period
 

st.set_page_config(
    page_title="Ostatnie treningi", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Ostatnie treningi")

alt.theme.enable("dark")

if "workouts_lw" not in st.session_state:
    st.session_state["workouts_lw"] = pd.read_csv("files/workouts.csv", sep='|').fillna('')
    st.session_state["workouts_lw"]["date"] = pd.to_datetime(st.session_state["workouts_lw"]["date"], format='%Y-%m-%d')

if "calendar_lw" not in st.session_state:
    st.session_state["calendar_lw"] = pd.read_csv("files/calendar.csv", sep='|')
    st.session_state["calendar_lw"]["date"] = pd.to_datetime(st.session_state["calendar_lw"]["date"], format='%Y-%m-%d')

if "min_date_lw" not in st.session_state:
    st.session_state["min_date_lw"] = st.session_state["calendar_lw"]['date'].min()

if "max_date_lw" not in st.session_state:
    st.session_state["max_date_lw"] = datetime.datetime.today().strftime(format='%Y-%m-%d')

if "counter" not in st.session_state:
    st.session_state["counter"] = 0


###############################################################################################
# sidebar options
###############################################################################################
# always use dates no greater than today
st.session_state["calendar_lw"] = filter_by_period(
    st.session_state["calendar_lw"],
    'date', st.session_state["calendar_lw"]['date'].min(),
    datetime.datetime.today().strftime(format='%Y-%m-%d')
)

with st.sidebar:   

    # select start year and month
    col_year_start, col_month_start = st.columns(2)
    with col_year_start:
        year_list_start = st.session_state["calendar_lw"]['year'].unique().tolist()
        selected_year_start = st.selectbox('Rok początkowy', year_list_start, index=0)
  
    with col_month_start:
        month_list_start = st.session_state["calendar_lw"].loc[
            st.session_state["calendar_lw"]['year'] == selected_year_start, ['month','month_name_pl']
        ].groupby(['month','month_name_pl']).all().reset_index()
        selected_month_start = st.selectbox('Miesiąc początkowy', month_list_start['month_name_pl'].tolist(), index = 0)
        selected_month_start_int = month_list_start.loc[month_list_start['month_name_pl'] == selected_month_start, 'month'].tolist()[0]


    # select end year and month
    col_year_end, col_month_end = st.columns(2)
    with col_year_end:
        year_list_end = st.session_state["calendar_lw"].loc[st.session_state["calendar_lw"]['year'] >= selected_year_start, 'year'].unique().tolist()
        selected_year_end = st.selectbox('Rok końcowy', year_list_end, index=len(year_list_end)-1)

    with col_month_end:
        if selected_year_end == selected_year_start:
            month_list_end = st.session_state["calendar_lw"].loc[
                (st.session_state["calendar_lw"]['year'] == selected_year_end) & 
                (st.session_state["calendar_lw"]['month'] >= selected_month_start_int)
                , 'month_name_pl'].unique().tolist()
        else:
            month_list_end = st.session_state["calendar_lw"].loc[(st.session_state["calendar_lw"]['year'] == selected_year_end), 'month_name_pl'].unique().tolist()
        selected_month_end = st.selectbox('Miesiąc końcowy', month_list_end, index=len(month_list_end)-1)


    # set min_date and max_date according to selected values
    selected_month_start_num = st.session_state["calendar_lw"][st.session_state["calendar_lw"]["month_name_pl"] ==  selected_month_start]['month_str'].unique()[0]
    selected_month_end_num = st.session_state["calendar_lw"][st.session_state["calendar_lw"]["month_name_pl"] ==  selected_month_end]['month_str'].unique()[0]
    min_day = '01'
    max_day = st.session_state["calendar_lw"][st.session_state["calendar_lw"]["month_name_pl"] ==  selected_month_end]['day_num'].unique()[0]

    st.session_state["min_date_lw"] = f"{selected_year_start}-{selected_month_start_num}-{min_day}"
    st.session_state["max_date_lw"] = f"{selected_year_end}-{selected_month_end_num}-{max_day}"


###############################################################################################
# options panel
###############################################################################################
def counter_plus():
    st.session_state["counter"] += 1

def counter_minus():
    st.session_state["counter"] -= 1

col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    prevoius = st.button("<", use_container_width=True,  on_click=counter_minus)

with col2:
    multiselect = st.selectbox(
        label="Wybierz sport",
        label_visibility='collapsed',
        options = ['siłownia', 'kalistenika', 'bieganie'],
        index=None,
        placeholder="Wybierz sport"
    )

with col3:
    next = st.button("\\>", use_container_width=True, on_click=counter_plus)


###############################################################################################
# preparing data & drawing table
###############################################################################################
chosen_columns = ['date', 'sport', 'exercise', 'details', 'comments']

if multiselect is not None:
    # prepare dataframe to show
    workouts = filter_by_period(
        st.session_state["workouts_lw"],
        'date',
        st.session_state['min_date_lw'],
        st.session_state['max_date_lw']
    )

    if multiselect == 'bieganie':
        w = workouts.loc[workouts['sport'] == multiselect, chosen_columns] \
            .sort_values('date', ascending=True) \
            .reset_index(drop = True)
        
    else:
        w = workouts.loc[workouts['sport'] == multiselect, chosen_columns] \
            .reset_index() \
            .groupby(chosen_columns).agg({'index' : 'max'}).reset_index() \
            .sort_values('index', ascending=True) \
            .reset_index(drop = True)
            
    if len(w) > 0:
        j = -1
        prev = w.loc[0, 'date']
        for i in range(len(w)):
            curr = w.loc[i, 'date']
            if prev != curr:
                j -= 1
            w.loc[i, 'index2'] = j
            prev = curr

        w['index2'] = w['index2'].astype(int)

        # make sure you cannot go out of range of activities
        st.session_state['counter'] = min(0, st.session_state['counter'])
        st.session_state['counter'] = max(w['index2'].min()+1, st.session_state['counter'])
        
        #print table
        df_print = w.loc[w['index2'] == (w['index2'].min() - st.session_state['counter']), ['date', 'exercise', 'details', 'comments']].reset_index(drop = True)
        df_print.columns = ['Data', 'Ćwiczenie', 'Szczegóły', 'Komentarze']
        st.table(df_print)
        st.markdown(f"Trening {-1 * w['index2'].min() + st.session_state['counter']} / {-1 * w['index2'].min()}")

    else:
        st.markdown("Brak treningów w tym okresie.")
