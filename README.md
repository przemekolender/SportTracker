# SportTracker

SportTracker is an app created to follow sport activites. It takes data from Google spreadshit and creates reports using Streamlit.

App is hosted on Streamlit cloud [\[link\]](https://sporttracker-oavru7obzni2dlhqj3date.streamlit.app/).

Data in the report is refreshed by localy running powershell scipt ***main.ps1***. It pulls code from remote, runs python code that downloads data from Google Drive, transfroms them to usable form and saves as .csv files. Finally powershell script pushes new data files to remote for Streamlit files to use. Logs from the process are saved in local file ***log.txt***.

To run report localy you have to run ***main.py*** with uncommented line 41.