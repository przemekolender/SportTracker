import pandas as pd
import re
import numpy as np
from data.data_processing import get_data, fill_data

class Workouts:
    
    def __init__(self) -> None:
        #load data
        self.workouts = get_data('Treningi 2024', 1)
        self.workouts.columns = ['index', 'date', 'sport', 'exercise', 'details', 'comments']

        # clear data
        self.workouts = fill_data(self.workouts, 'index')
        self.workouts = fill_data(self.workouts, 'date')
        self.workouts = fill_data(self.workouts, 'sport')

        # calculate usable results
        self.calculate_run_distnace()
        self.calculate_run_time()
        self.unify_sets_convenction()
        self.split_weights()
        self.calcualte_reps_sum()
        self.calculate_kilos_sum()

        self.workouts['date'] = pd.to_datetime(self.workouts['date'], format='%Y-%m-%d')


    ###############################################################################################
    # adds column with integer number of km runned
    ###############################################################################################
    def calculate_run_distnace(self):
        self.workouts['distance_km'] = self.workouts[
                (self.workouts['sport'] == 'bieganie') & (self.workouts['exercise'] == 'dystans')
            ]['details'] \
            .apply(lambda x : str(x).replace('km', '')) \
            .apply(lambda x : str(x).replace(' ', '')) \
            .astype(float) 
        
        self.workouts['distance_km'] = self.workouts['distance_km'].fillna(0)


    ###############################################################################################
    # adds columns with integer number of hours, minutes and seconds spent on running
    ###############################################################################################
    def calculate_run_time(self):
        self.workouts['run_hours'] = self.workouts[
            (self.workouts['sport'] == 'bieganie') & (self.workouts['exercise'] == 'czas')
            ]['details'].apply(lambda x : x[0:2]).astype(int)
        
        self.workouts['run_minutes'] = self.workouts[
            (self.workouts['sport'] == 'bieganie') & (self.workouts['exercise'] == 'czas')
            ]['details'].apply(lambda x : x[3:5]).astype(int)
        
        self.workouts['run_seconds'] = self.workouts[
            (self.workouts['sport'] == 'bieganie') & (self.workouts['exercise'] == 'czas')
            ]['details'].apply(lambda x : x[6:8]).astype(int)
        
        self.workouts['run_hours'] = self.workouts['run_hours'].fillna(0)
        self.workouts['run_minutes'] = self.workouts['run_minutes'].fillna(0)
        self.workouts['run_seconds'] = self.workouts['run_seconds'].fillna(0)
        self.workouts['run_total_seconds'] = self.workouts['run_hours'] * 3600 + self.workouts['run_minutes'] * 60 + self.workouts['run_seconds']
    

    ###############################################################################################
    # if set is written as 'x10' add '1', so we have '1x10'
    ###############################################################################################
    def unify_sets_convenction(self):
        ex = get_data('Treningi 2024', 2)
        time_exercises = ex[ex['opis'] == 'na czas']['ćwiczenie'].to_list()
        self.workouts['details_fixed'] = self.workouts['details'] \
            .apply(lambda x : re.sub(r' x', r' 1x', str(x))) \
            .apply(lambda x : re.sub(r'^x', r'1x', str(x)))
        
        self.workouts.loc[self.workouts['exercise'].isin(time_exercises), 'details_fixed'] = ''
        self.workouts.loc[self.workouts['sport'] == 'bieganie', 'details_fixed'] = ''
        


    ###############################################################################################
    # splits rows with various weights used so there is only 1 weight in one row
    ###############################################################################################
    def split_weights(self):
        new_rows = pd.DataFrame(columns=self.workouts.columns)
        for i in range(len(self.workouts)):
            if ';' in self.workouts.loc[i, 'details_fixed']:
                weights = self.workouts.loc[i, 'details_fixed'].split(';')
                for weight in weights:
                    row = self.workouts.loc[i, :]
                    row_df = pd.DataFrame(row).transpose().reset_index(drop=True)
                    row_df.loc[0, 'details_fixed'] = weight
                    new_rows = pd.concat([new_rows, row_df], axis=0, ignore_index=True)
            else:
                new_rows = pd.concat([new_rows, pd.DataFrame(self.workouts.loc[i, :]).transpose()], axis=0, ignore_index=True)

        self.workouts = new_rows.reset_index(drop = True)


    ###############################################################################################
    # adds column with intiger number of repetitions
    ###############################################################################################
    def calcualte_reps_sum(self):
        def find_sum_reps(arr):
            arr_int = []
            for i in arr:
                arr_str = i.split('x')
                reps = int(arr_str[0]) * int(arr_str[1])
                arr_int.append(reps)
            return sum(arr_int)

        self.workouts['reps_sum'] = self.workouts['details_fixed'] \
            .apply(lambda x : re.findall(r'[\d]+x[\d]+', str(x))) \
            .apply(lambda x : find_sum_reps(x)) \
            .astype(int)


    ###############################################################################################
    # adds column with intiger number of kilograms used and column with kilograms lifted 
    ###############################################################################################
    def calculate_kilos_sum(self):
        def find_weight(s):
            arr = re.findall(r'[\d]+\.[\d]+kg|[\d]+kg', str(s))
            if len(arr) == 0:
                return '0'
            else:
                return str(arr[0]).replace('kg', '')

        self.workouts['weight'] = self.workouts['details_fixed'] \
            .apply(lambda x : find_weight(x)) \
            .astype(float)
        
        self.workouts['weights_lifted'] = self.workouts['weight'] * self.workouts['reps_sum']

