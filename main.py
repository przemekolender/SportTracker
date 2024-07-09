from data.workouts import Workouts
import os


def main():
    os.system("streamlit run streamlit/app.py")


if __name__ == "__main__":
    if "workouts.csv" in os.listdir():
        os.remove("workouts.csv")
    w = Workouts()
    main()
