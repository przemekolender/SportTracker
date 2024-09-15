# SportTracker

SportTracker is an app created to follow sport activites. I takes data from Google spreadshit and creates reports using Streamlit.

App is hosted on Streamlit cloud [\[link\]](https://sporttracker-qnxrkg9i2dtjunkujr4mwk.streamlit.app/).

Streamlit cloud hosts appilication basing on branch ***prod*** from this repository. Branch main is used for development. 

Data in the report is refreshed by localy running powershell scipt ***main.ps1***. It pulls branch prod, runs python code that downloads data from Google Drive, transfroms them to usable form and saves as .csv files. Finally powershell script pushes new data files to branch prod. Logs from the process are saved in local file ***log.txt***.

To run report localy you have to run ***main.py*** with uncommented line 26.