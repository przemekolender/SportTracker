import streamlit as st
import pandas as pd
import altair as alt
#import plotly.express as px

st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="expanded"
)

alt.themes.enable("dark")

with st.sidebar:
    st.title('🏂 US Population Dashboard')
    
    year_list = list(['2023', '2024'])[::-1]
    
    selected_year = st.selectbox('Select a year', year_list, index=len(year_list)-1)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)