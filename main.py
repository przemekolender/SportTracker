from data.workouts import Workouts
from data.data_processing import load_calendar, get_data
import os


def main():
    os.system("streamlit run streamlit/app.py")


if __name__ == "__main__":
    for file in os.listdir("files"):
        os.remove(f"files/{file}")

    w = Workouts()
    w.workouts.to_csv("files/workouts.csv")
    
    calendar = load_calendar()
    calendar.to_csv("files/calendar.csv")

    exercises = get_data("Treningi 2024", 2)
    exercises.to_csv("files/exercises.csv")

    sports = get_data("Treningi 2024", 3)
    sports.to_csv("files/sports.csv")

    main()
