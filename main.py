from data.workouts import Workouts
from data.data_processing import load_calendar, get_data
import os
import pandas as pd
from datetime import datetime


def main():
    print(f"Removing old files {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n")
    for file in os.listdir("files"):
        if '.csv' in file:
            os.remove(f"files/{file}")

    print(f"Downloading sports.csv {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n")
    sports = get_data("Treningi", 0)
    sports.columns = ['sport','category', 'isdistance', 'sport_color', 'sport_category_color', 'event_color', 'run_work']
    sports.to_csv("files/sports.csv", sep='|')

    print(f"Downloading workouts 2023 {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n")
    w2023 = Workouts('Treningi', 5)
    print(f"Downloading workouts 2024 {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n")
    w2024 = Workouts('Treningi', 3)

    print(f"Preparing full file workouts.csv {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n")
    w = pd.concat(
        [w2023.workouts, w2024.workouts], ignore_index=True
    ).reset_index(drop = True)
    w.to_csv("files/workouts.csv", sep='|')
    
    print(f"Downloading calendar 2023 {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n")
    c2023 = load_calendar('Treningi', 4)
    print(f"Downloading calendar 2024 {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n")
    c2024 = load_calendar('Treningi', 2)

    print(f"Preparing full file calendar.csv {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n")
    calendar = pd.concat(
        [c2023, c2024], ignore_index=True
    ).reset_index(drop = True)
    calendar.to_csv("files/calendar.csv", sep='|')

    #os.system("streamlit run streamlit/app.py")


if __name__ == "__main__":  
    main()
