import pandas as pd
import re
import numpy as np
from data.data_processing import get_data, fill_data, filter_by_period

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
        pass


    ###############################################################################################
    # if set is written as 'x10' add '1', so we have '1x10'
    ###############################################################################################
    def unify_sets_convenction(self):
        pass


    ###############################################################################################
    # splits rows with various weights used so there is only 1 weight in one row
    ###############################################################################################
    def split_weights(self):
        pass


    ###############################################################################################
    # adds column with intiger number of repetitions
    ###############################################################################################
    def calcualte_reps_sum(self):
        pass


    ###############################################################################################
    # adds column with intiger number of kilograms used and column with kilograms lifted 
    ###############################################################################################
    def calculate_kilos_sum(self):
        pass


    ###############################################################################################
    # returns running distnace in the time interval
    ###############################################################################################
    def run_distance(self, start_date='0001-01-01', end_date='9999-12-31') -> float:
        _workouts = filter_by_period(self.workouts, 'date', start_date, end_date)
        return float(_workouts['distance_km'].sum()).__round__(2)


    ###############################################################################################
    # returns running time in the time interval
    ###############################################################################################
    def run_time(self, start_date, end_date):
        pass


    ###############################################################################################
    # returns number of repetitions in the time interval
    ###############################################################################################
    def reps_sum(self, start_date, end_date) -> int:
        pass


    ###############################################################################################
    # returns number of kilos lifted in the time interval
    ###############################################################################################
    def kilos_sum(self, start_date, end_date) -> int:
        pass


    ###############################################################################################
    # returns biggest weight lifted in given exercise
    ###############################################################################################
    def best_weight(self) -> float:
        pass


    ###############################################################################################
    # returns most reps done in given exercise
    ###############################################################################################
    def most_reps(self) -> int:
        pass

