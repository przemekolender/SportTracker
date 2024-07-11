import pandas as pd
import calplot
import plotly.express as px

def calendar_heatmap(data):
    pass

def month_workout_number(data):
    fig = px.line(data, x = "month", y = "counts", line_shape='spline', markers=True)
    fig.update_layout(
        plot_bgcolor='white'
    )
    return fig