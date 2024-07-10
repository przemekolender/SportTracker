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


##
#
##
def create_date_dim(dates):
    #months = ['-', 'Styczeń','Luty','Marzec','Kwiecień','Maj','Czerwiec','Lipiec','Sierpień','Wrzesień','Październik','Listopad','Grudzień']
    months_days = {'-' : 31,'Styczeń' : 31,'Luty' : 28,'Marzec' : 31,'Kwiecień' : 30,
                   'Maj' : 31,'Czerwiec' : 30,'Lipiec' :31,'Sierpień':31,
                   'Wrzesień':30,'Październik':31,'Listopad':30,'Grudzień':31}
    

    dim_date = pd.DataFrame(dates.unique(), columns=['date'])
    dim_date.loc[:, 'year'] = dim_date['date'].apply(lambda x : x[0:4]).astype(int)
    dim_date.loc[:, 'month'] = dim_date['date'].apply(lambda x : x[5:7]).astype(int)
    dim_date.loc[:, 'month_str'] = dim_date['date'].apply(lambda x : x[5:7])
    dim_date.loc[:, 'day'] = dim_date['date'].apply(lambda x : x[8:10]).astype(int)
    dim_date.loc[:, 'day_str'] = dim_date['date'].apply(lambda x : x[8:10])
    dim_date.loc[:, 'month_name'] = dim_date['month'].apply(lambda x : list(months_days.keys())[x])
    dim_date.loc[:, 'day_num'] = dim_date['month_name'].apply(lambda x : months_days[x])

    return dim_date