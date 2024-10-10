import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import re
import numpy as np


###############################################################################################
# load data from Google sheet
###############################################################################################
def get_data(sheet_name, sheet_id):
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('sporttracker-key.json', scope)

    # authorize the clientsheet 
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open(sheet_name)

    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(sheet_id)
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)

    return records_df


###############################################################################################
# fill empty rows with index, date and training name
###############################################################################################
def fill_data(df, column_name):
    n = df.shape[0]
    index = str(df.loc[0, column_name]).replace(' ', '')
    for i in range(n):
        if df.loc[i, column_name] == '':
            df.loc[i, column_name] = index
        else: 
            index = str(df.loc[i, column_name]).replace(' ', '')
            df.loc[i, column_name] = index
    return df


###############################################################################################
# filter by date using start and end
###############################################################################################
def filter_by_period(df, column_name, start_date = '0001-01-01', end_date = '9999-12-31'):
    #df[column_name] = pd.to_datetime(df[column_name])
    return df[(pd.to_datetime(df[column_name]) >= start_date) & (pd.to_datetime(df[column_name]) <= end_date)]


###############################################################################################
# find most reps of given exercise
###############################################################################################
def help_most_reps(arr):
    reps = []
    for detail in arr:
        reps_str = re.findall(r'x[\d]+', str(detail))
        for rep_str in reps_str:
            reps.append(int(rep_str.replace('x', '')))
    if len(reps) == 0:
        return 0
    else:
        return max(reps)


###############################################################################################
# returns running distnace in the time interval
###############################################################################################
def run_distance(workouts, start_date='0001-01-01', end_date='9999-12-31') -> float:
    #_workouts = filter_by_period(workouts, 'date', start_date, end_date)
    return float(workouts['distance_km'].sum()).__round__(2)


###############################################################################################
# returns running time in the time interval
###############################################################################################
def run_time(workouts, start_date='0001-01-01', end_date='9999-12-31'):
    #_workouts = filter_by_period(workouts, 'date', start_date, end_date)
    s = workouts['run_total_seconds'].sum()
    return int(s // 3600), int((s % 3600) // 60), int(s % 60)


###############################################################################################
# returns number of repetitions in the time interval
###############################################################################################
def reps_sum(workouts, exercise = '', start_date='0001-01-01', end_date='9999-12-31') -> int:
     #_workouts = filter_by_period(workouts, 'date', start_date, end_date)
     if exercise == '':
        return int(workouts['reps_sum'].sum())
     else:
        return int(workouts[workouts['exercise'] == exercise]['reps_sum'].sum())
     

###############################################################################################
# returns number of kilos lifted in the time interval
###############################################################################################
def kilos_sum(workouts, exercise = '', start_date='0001-01-01', end_date='9999-12-31') -> int:
    #_workouts = filter_by_period(workouts, 'date', start_date, end_date)
    if exercise == '':
        return int(workouts['weights_lifted'].sum())
    else:
        return int(workouts[workouts['exercise'] == exercise]['weights_lifted'].sum())


###############################################################################################
# returns biggest weight lifted in given exercise
###############################################################################################
def best_weight(workouts, exercise = '', start_date='0001-01-01', end_date='9999-12-31'):
    #_workouts = filter_by_period(workouts, 'date', start_date, end_date)
    max_weight = workouts[workouts['exercise'] == exercise]['weight'].max()
    if pd.isna(max_weight):
        return 0, 0
    reps = workouts[(workouts['exercise'] == exercise) & (workouts['weight'] == max_weight)]['reps'].max()
    return float(max_weight), int(reps)


###############################################################################################
# returns most reps done in given exercise
###############################################################################################
def most_reps(workouts, exercise = '', start_date='0001-01-01', end_date='9999-12-31'):
    #_workouts = filter_by_period(workouts, 'date', start_date, end_date)
    reps = workouts[workouts['exercise'] == exercise]['reps'].max()
    if pd.isna(reps):
        return 0
    else:
        return int(reps)
       

###############################################################################################
# helper function to get str of day in month / month number: 3 -> 03
###############################################################################################
def int_to_str(x : int):
    if x < 10:
        return '0' + str(x)
    else:
        return str(x)
    

###############################################################################################
# helper function to print time in nice formatting
###############################################################################################
def hour_str(x : int):
    h = int_to_str(x // 3600)
    m = int_to_str((x % 3600) // 60)
    s = int_to_str(x % 60)
    return f"{h}:{m}:{s}"


###############################################################################################
# create df with information about dates
###############################################################################################
def create_date_dim(dates):   
    dim_date = pd.DataFrame(dates.unique(), columns=['date'])
    dim_date['date'] = pd.to_datetime(dim_date['date'], format='%Y-%m-%d')
    dim_date.loc[:, 'year'] = dim_date['date'].apply(lambda x : x.year)
    dim_date.loc[:, 'month'] = dim_date['date'].apply(lambda x : x.month)
    dim_date.loc[:, 'month_str'] = dim_date['date'].apply(lambda x : int_to_str(x.month))
    dim_date.loc[:, 'day'] = dim_date['date'].apply(lambda x : x.day)
    dim_date.loc[:, 'day_str'] = dim_date['date'].apply(lambda x : int_to_str(x.day))
    dim_date.loc[:, 'month_name_en'] = dim_date['date'].apply(lambda x : x.month_name())
    dim_date.loc[:, 'month_name_pl'] = dim_date['date'].apply(lambda x : x.month_name(locale='pl_PL'))
    dim_date.loc[:, 'day_num'] = dim_date['date'].apply(lambda x : x.daysinmonth)
    dim_date.loc[:, 'day_of_week'] = dim_date['date'].apply(lambda x : x.day_of_week + 1)
    dim_date.loc[:, 'day_of_week_name_en'] = dim_date['date'].apply(lambda x : x.day_name())
    dim_date.loc[:, 'day_of_week_name_pl'] = dim_date['date'].apply(lambda x : x.day_name(locale='pl_PL'))
    dim_date.loc[:, 'week'] = dim_date['date'].apply(lambda x : x.week)
    dim_date.loc[:, 'day_of_year'] = dim_date['date'].apply(lambda x : x.day_of_year)
    dim_date.loc[:, 'year_month_day'] = (dim_date['year'].astype(str) + dim_date['month_str'] + dim_date['day_str']).astype(int)
    dim_date.loc[:, 'year_month'] = (dim_date['year'].astype(str) + dim_date['month_str']).astype(int)
    dim_date.loc[:, 'year_week'] = (dim_date['year'].astype(str) + dim_date['week'].apply(lambda x : int_to_str(x))).astype(int)
    dim_date.loc[(dim_date['month'] == 12) & (dim_date['week'] == 1), 'year_week'] = ((dim_date['year']+1).astype(str) + dim_date['week'].apply(lambda x : int_to_str(x))).astype(int)
    dim_date.loc[(dim_date['month'] == 1) & (dim_date['week'] > 5), 'year_week'] = ((dim_date['year']-1).astype(str) + dim_date['week'].apply(lambda x : int_to_str(x))).astype(int)
    dim_date.loc[:, 'fake_month_date'] = pd.to_datetime(dim_date['year'].astype(str) + '-' + dim_date['month_str'] + '-01')

    week_start = dim_date.loc[dim_date['day_of_week_name_en'] == 'Monday', :]
    week_start = week_start[['year_week', 'date']]
    week_start.rename(columns = {'date' : 'week_start_date'}, inplace=True)
    dim_date = dim_date.merge(
        right = week_start,
        on = 'year_week',
        how = 'left'
    )

    week_end = dim_date.loc[dim_date['day_of_week_name_en'] == 'Sunday', :]
    week_end = week_end[['year_week', 'date']]
    week_end.rename(columns = {'date' : 'week_end_date'}, inplace=True)
    dim_date = dim_date.merge(
        right = week_end,
        on = 'year_week',
        how = 'left'
    )

    dim_date.loc[dim_date['week_start_date'].isnull(), 'week_start_date'] = pd.to_datetime(dim_date.loc[dim_date['week_start_date'].isnull(), 'week_end_date']) + pd.DateOffset(days=-6)
    dim_date.loc[dim_date['week_end_date'].isnull(), 'week_end_date'] = pd.to_datetime(dim_date.loc[dim_date['week_end_date'].isnull(), 'week_start_date']) + pd.DateOffset(days=6)
    
    return dim_date


###############################################################################################
# load data from tab calendar
###############################################################################################
def load_calendar(sheet_name, sheet_id):
    calnedar = get_data(sheet_name, sheet_id)
    calnedar.columns = ['index', 'date', 'week_day', 'sport', 'time']
    calnedar['date'] = pd.to_datetime(calnedar['date'], format='%d.%m.%Y')
    calnedar['info'] = calnedar['date'].apply(lambda x : str(x)[:10]+', ') + calnedar['sport']
    calnedar.loc[calnedar['sport'] == '', 'info'] = ''
    calnedar.loc[calnedar['time'] == '', 'time'] = '00:00:00'
    calnedar['hours'] = calnedar['time'].apply(lambda x : str(x)[:2]).astype(int)
    calnedar['minutes'] = calnedar['time'].apply(lambda x : str(x)[3:5]).astype(int)
    calnedar['seconds'] = calnedar['time'].apply(lambda x : str(x)[6:8]).astype(int)
    calnedar['total_seconds'] = calnedar['hours'] * 3600 + calnedar['minutes'] * 60 + calnedar['seconds']

    sports = pd.read_csv("files/sports.csv", sep = "|")[['sport', 'category', 'isdistance']]
    calnedar = calnedar.merge(
        right = sports,
        on = 'sport',
        how = 'left'
    )

    #calnedar['date_str'] = calnedar['date'].astype(str)
    dim_date = create_date_dim(calnedar['date'])
    calnedar = pd.merge(
        left=calnedar,
        right=dim_date,
        left_on= 'date',
        right_on='date',
        how='left'
    )

    return calnedar


###############################################################################################
# distance and time of runs are in separate rows - make df where there is one row per run
###############################################################################################
def transpose_runs(runs):
    runs = runs[runs['exercise'].isin(['dystans', 'tempo', 'czas'])].reset_index(drop=True)
    e = 0
    entity_id = []
    for i in range(runs.shape[0]):
        if runs['exercise'][i] == 'dystans':
            e += 1
        entity_id.append(e)

    runs['entity_id'] = entity_id

    d = runs.loc[runs['exercise'] == 'dystans', ['date', 'exercise', 'distance_km', 'entity_id', 'sport']]
    p = runs.loc[runs['exercise'] == 'tempo', ['details', 'entity_id']]
    p.rename(columns = {'details' : 'pace'}, inplace=True)
    t = runs.loc[runs['exercise'] == 'czas', ['details', 'run_hours', 'run_minutes', 'run_seconds', 'run_total_seconds', 'entity_id']]
    t.rename(columns = {'details' : 'time'}, inplace=True)

    return d.merge(p, on='entity_id', how='inner').merge(t, on='entity_id', how='inner')

    
###############################################################################################
# returns time and pace of the best run on the given distance as strings
###############################################################################################
def best_run(workouts, distance):
    runs = workouts[workouts['sport'] == 'bieganie']
    runs_t = transpose_runs(runs)
    runs_t = runs_t.loc[runs_t['distance_km'] == distance, :].sort_values(by = 'run_total_seconds', ascending = True).reset_index(drop = True).head(1)
    return str(runs_t.loc[0, 'time']), str(runs_t.loc[0, 'pace'])


###############################################################################################
# returns best run on the given or longer distance as df
###############################################################################################
def best_run_approx(workouts, distance):
    runs = workouts[workouts['sport'] == 'bieganie']
    runs_t = transpose_runs(runs)
    runs_t['pace_float'] = runs_t['pace'].str.replace('\'', '.').astype(float)
    runs_t = runs_t.loc[runs_t['distance_km'] >= distance, :].sort_values(by = 'pace_float', ascending = True).reset_index(drop = True).head(1)
    return runs_t.loc[:, ['date', 'distance_km', 'pace', 'time']]


###############################################################################################
# returns pallete in form of dictionary from pandas df
###############################################################################################
def create_pallete(df, key_column, value_column):
    df = df.groupby([key_column, value_column]).size().reset_index()
    df.index = df[key_column]
    return df[value_column].to_dict()

