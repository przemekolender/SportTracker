import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import re
import numpy as np


###########################################################
# load data from Google sheet
###########################################################
def get_data(sheet_name, sheet_id):
    # define the scope
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('../sporttracker-key.json', scope)

    # authorize the clientsheet 
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open(sheet_name)

    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(sheet_id)
    records_data = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)

    return records_df





###########################################################
# fill empty rows with index, date and training name
###########################################################
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


###########################################################
# filter by date using start and end
###########################################################
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


###########################################################
# calculate number of kilometers runned
###########################################################
def sum_run_distance(df, start_date, end_date):
    df = filter_by_period(df, start_date, end_date)
    s = df[(df['sport'] == 'bieganie') & (df['exercise'] == 'dystans')]['details'] \
        .apply(lambda x : str(x).replace('km', '')) \
        .apply(lambda x : str(x).replace(' ', '')) \
        .astype(float) \
        .sum()
    
    return float(s)


###########################################################
# calculate running time
###########################################################
def sum_run_time(df, start_date, end_date):
    df = filter_by_period(df, start_date, end_date)
    df_ = df[(df['sport'] == 'bieganie') & (df['exercise'] == 'czas')].reset_index(drop = True)
    df_['h'] = df_['details'].apply(lambda x : x[0:2]).astype(int)
    df_['m'] = df_['details'].apply(lambda x : x[3:5]).astype(int)
    df_['s'] = df_['details'].apply(lambda x : x[6:8]).astype(int)
    df_['total_s'] = df_['h'] * 3600 + df_['m'] * 60 + df_['s']
    s = df_['total_s'].sum()
    
    return int(s // 3600), int((s % 3600) // 60), int(s % 60)



def find_sum_reps(arr):
    arr_int = []
    for i in arr:
        arr_int.append(int(str(i).replace('x', '')))
    return sum(arr_int)


def find_sum_reps_concat(arr):
    arr_int = []
    for i in arr:
        arr_str = i.split('x')
        reps = int(arr_str[0]) * int(arr_str[1])
        arr_int.append(reps)
    return sum(arr_int)


def sum_reps(df, start_date, end_date):
    df = filter_by_period(df, start_date, end_date)
    df['reps1'] = df['details'] \
        .apply(lambda x : re.findall(r'x[\d]+', str(x))) \
        .apply(lambda x : find_sum_reps(x))
    
    df['reps2'] = df['details'] \
        .apply(lambda x : re.findall(r'[\d]+x[\d]+', str(x))) \
        .apply(lambda x : find_sum_reps_concat(x))
    
    df['final_reps'] = np.where(df['reps2'] == 0, df['reps1'], df['reps2'])

    ex = get_data('Treningi 2024', 2)

    df_ = pd.merge(
        left=df,
        right=ex,
        left_on='exercise',
        right_on = 'ćwiczenie',
        how = 'inner'
    )
    df_['final_reps'] = np.where(df_['opis'] == 'na czas', 0, df_['final_reps'])
    df_['final_reps'] = np.where(df_['sport_x'] == 'bieganie', 0, df_['final_reps'])

    return df_, int(df_['final_reps'].sum())
    

def sum_kilos(sets):
    res = 0
    for w in sets:
        weights = re.findall(r'[\d]+kg', w)
        if len(weights) == 1:
            weigth = int(weights[0].replace('kg', ''))
            #reps = find_sum_reps(re.findall(r'x[\d]+', str(w)))
            reps2 = find_sum_reps_concat(re.findall(r'[\d]+x[\d]+', str(w)))

            res = res + weigth * reps2

    return res