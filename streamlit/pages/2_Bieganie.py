# running

import streamlit as st

st.set_page_config(
    page_title="Bieganie", 
    page_icon="🏋️‍♀️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("# Bieganie")



#distnace = run_distance(workouts)
#st.metric(label="Total run distnace", value=f"{distnace} km")
#
#h,m,s = run_time(workouts)
#st.metric(label="Total run time", value=f"{h} hours {m} minutes {s} seconds")
#
#reps = reps_sum(workouts)
#st.metric(label="Total reps", value=reps)
#
#kilos = kilos_sum(workouts)
#st.metric(label="Total kilos lifted", value=kilos)