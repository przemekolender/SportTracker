from data.workouts import Workouts
from data.data_processing import load_calendar, get_data
import os


def main():
    for file in os.listdir("files"):
        if '.csv' in file:
            os.remove(f"files/{file}")

    w = Workouts()
    w.workouts.to_csv("files/workouts.csv")
    
    calendar = load_calendar()
    calendar.to_csv("files/calendar.csv")

    #os.system("streamlit run streamlit/app.py")


if __name__ == "__main__":  
    main()
