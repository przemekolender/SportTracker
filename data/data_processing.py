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
    df[column_name] = pd.to_datetime(df[column_name])
    return df[(df[column_name] >= start_date) & (df[column_name] <= end_date)]


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
    details = workouts[(workouts['exercise'] == exercise) & (workouts['weight'] == max_weight)]['details_fixed'].to_list()
    reps = help_most_reps(details)
    return float(max_weight), reps


###############################################################################################
# returns most reps done in given exercise
###############################################################################################
def most_reps(workouts, exercise = '', start_date='0001-01-01', end_date='9999-12-31'):
    #_workouts = filter_by_period(workouts, 'date', start_date, end_date)
    details = workouts[workouts['exercise'] == exercise]['details_fixed'].to_list()
    reps = help_most_reps(details)
    return reps


###############################################################################################
# helper function to get str of day in month / month number: 3 -> 03
###############################################################################################
def int_to_str(x : int):
    if x < 10:
        return '0' + str(x)
    else:
        return str(x)


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

    return dim_date


###############################################################################################
# load data from tab calendar
###############################################################################################
def load_calendar():
    calnedar = get_data('Treningi 2024', 0)
    calnedar.columns = ['index', 'date', 'week_day', 'sport']
    calnedar['date'] = pd.to_datetime(calnedar['date'], format='%d.%m.%Y')
    calnedar['info'] = calnedar['date'].apply(lambda x : str(x)[:10]+', ') + calnedar['sport']
    calnedar.loc[calnedar['sport'] == '', 'info'] = ''
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


def data_month_workout_number(calendar):
    return calendar[calendar['sport'] != ''][['month']] \
        .groupby(by = 'month') \
        .size() \
        .reset_index(name='counts')
    