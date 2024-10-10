from data.workouts import Workouts
from data.data_processing import load_calendar, get_data
import os
import pandas as pd


def main():
    for file in os.listdir("files"):
        if '.csv' in file:
            os.remove(f"files/{file}")

    sports = get_data("Treningi", 0)
    sports.columns = ['sport','category', 'isdistance', 'sport_color', 'sport_category_color', 'event_color', 'run_work']
    sports.to_csv("files/sports.csv", sep='|')

    w2023 = Workouts('Treningi', 5)
    w2024 = Workouts('Treningi', 3)
    w = pd.concat(
        [w2023.workouts, w2024.workouts], ignore_index=True
    ).reset_index(drop = True)
    w.to_csv("files/workouts.csv", sep='|')
    
    c2023 = load_calendar('Treningi', 4)
    c2024 = load_calendar('Treningi', 2)
    calendar = pd.concat(
        [c2023, c2024], ignore_index=True
    ).reset_index(drop = True)
    calendar.to_csv("files/calendar.csv", sep='|')

    #os.system("streamlit run streamlit/app.py")


if __name__ == "__main__":  
    main()
