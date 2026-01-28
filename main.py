from data.workouts import Workouts
from data.data_processing import load_calendar, get_data
import os
import pandas as pd
from datetime import datetime

def log(message):
    print(f"{message} {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}\n")


def main():
    log("Removing old files")
    for file in os.listdir("files"):
        if '.csv' in file:
            os.remove(f"files/{file}")

    log("Downloading sports.csv")
    sports = get_data("Treningi", 0)
    sports.columns = ['sport','category', 'isdistance', 'sport_color', 'sport_category_color', 'event_color', 'run_work']
    sports.to_csv("files/sports.csv", sep='|')

    log("Downloading workouts 2023")
    w2023 = Workouts('Treningi', 9)
    log("Downloading workouts 2024")
    w2024 = Workouts('Treningi', 7)
    log("Downloading workouts 2025")
    w2025 = Workouts('Treningi', 5)
    log("Downloading workouts 2026")
    w2026 = Workouts('Treningi', 3)

    log("Preparing full file workouts.csv")
    w = pd.concat(
        [w2023.workouts, w2024.workouts, w2025.workouts, w2026.workouts], ignore_index=True
    ).reset_index(drop = True)
    w.to_csv("files/workouts.csv", sep='|')
    
    log("Downloading calendar 2023")
    c2023 = load_calendar('Treningi', 8)
    log("Downloading calendar 2024")
    c2024 = load_calendar('Treningi', 6)
    log("Downloading calendar 2025")
    c2025 = load_calendar('Treningi', 4)
    log("Downloading calendar 2026")
    c2026 = load_calendar('Treningi', 2)

    log("Preparing full file calendar.csv")
    calendar = pd.concat(
        [c2023, c2024, c2025, c2026], ignore_index=True
    ).reset_index(drop = True)
    calendar.to_csv("files/calendar.csv", sep='|')

    #os.system("streamlit run streamlit/app.py")


if __name__ == "__main__":  
    main()
