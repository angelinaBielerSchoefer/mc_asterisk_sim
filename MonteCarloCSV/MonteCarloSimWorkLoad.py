import random
from datetime import date, datetime, timedelta
from operator import truediv
from statistics import stdev

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from contourpy.util.data import simple
from fontTools.subset import remap
from matplotlib.colors import cnames
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import pandas as pd

import os

from Prediction import Prediction


class MonteCarloSimWorkLoad:



    def __init__(self, save_charts = False, trials=1000):
        self.trials = trials
        self.save_charts = save_charts
        self.numSubSet = 1000

        script_dir = os.path.dirname(os.path.abspath(__file__))


    #### SIM 2 Workload
    def initWorkLoadSim(self, numWorkLoadItems, precision = 0.005):
        self.numDataSets = numWorkLoadItems
        self.precision = precision
        # Save the plot as an image in the "Charts" folder within working directory
        self.charts_folder = os.path.join(os.getcwd(), 'Charts_SIM2')
        if self.save_charts and not os.path.exists(self.charts_folder):
            os.makedirs(self.charts_folder)

    #### SIM 2 Workloads
    def create_workload_occurance(self, storypoints_minutes_map):
        self.storypoints_per_minute = []
        self.minutes_per_storypoint=[]
        sp_category = [1, 2, 4, 7, 16]


        for workload in storypoints_minutes_map:
            sp_per_min = float(workload.story_point) / float(workload.time_spend)
            min_pre_sp = float(workload.time_spend) / float(workload.story_point)
            self.storypoints_per_minute.append(sp_per_min)
            self.minutes_per_storypoint.append(min_pre_sp)

            if (workload.story_point not in sp_category):
                sp_category.append(workload.story_point)



        self.mean_minutes_and_stdev_per_sp_category = pd.DataFrame(columns=['mean min','stdev min', 'cnt occ'],index=sp_category)

        for cat in sp_category:

            minutes_sub_liste = [workload.time_spend for workload in storypoints_minutes_map if workload.story_point == cat]
            mean_min = sum(minutes_sub_liste) / len(minutes_sub_liste)
            stdev_min = stdev(minutes_sub_liste)
            cnt_occ = len(minutes_sub_liste)

            self.mean_minutes_and_stdev_per_sp_category.loc[cat] = [mean_min,stdev_min,cnt_occ]

        print("MonteCarloService: Workload Simulation (2) prepared")
        return self.storypoints_per_minute, self.minutes_per_storypoint, self.mean_minutes_and_stdev_per_sp_category

########################### SIM When will Storypoints be finalized ####################################
    def when_storypoints_finalized(self,remainig_storypoints, prediction_map=None):
        print("--------------------------------")
        print("Running Monte Carlo Simulation 2 - Predict the Time in Minutes to finalize {0} StoryPoint".format(remainig_storypoints))
        print("--------------------------------")
        precision = 1 # The Range around the true value, pending on the circumstances
        the_confidence_divider = 1.96 # given by gaussian a normal distributiion within above range hast 95% confidence if range is devided by this
        stdev_min = 2
        mc_mean_min ={}
        numSubSet_toPrint = numSubSet = self.numSubSet
        while stdev_min > precision/the_confidence_divider:
            mc_mean_min = self.__run_mc_minutes_to_finalize_one_sp(numSubSet)
            mean_occ = sum (mc_mean_min.keys())/len(mc_mean_min)
            numSubSet_toPrint = numSubSet
            numSubSet *= 2
            if (stdev_min != stdev(mc_mean_min.keys())):
                stdev_min = stdev(mc_mean_min.keys())

            else:
                break
        min = round((sum(mc_mean_min.keys())/len(mc_mean_min)) - stdev_min,3)
        max = round((sum(mc_mean_min.keys())/len(mc_mean_min)) + stdev_min,3)
        print ("Validity Check of MC result: One Story Point is finalized within {0} and {1} minutes with a confidence of 95 % by using {2} Data points".format(min, max, numSubSet_toPrint))

        #mc_result = self.__run_mc_minutes_to_finalize(remainig_storypoints)

        prediction_map = self.__get_prediction_minutes_to_finalize(mc_mean_min,remainig_storypoints, None)#,prediction_map)
        return prediction_map
    def __run_mc_minutes_to_finalize_one_sp(self, numSubSet):
        results = {}

        #try for several times to minimize the possibility of bad luck
        for i in range(self.trials):

            #randomize the entries of self.storypoints_per_minute
            #rand_sp_per_min = self.__prepare_random_sorting_of()

            working_data_set = self.minutes_per_storypoint.copy()

            while len(working_data_set) < numSubSet:
                working_data_set.extend(self.minutes_per_storypoint)

            subset = random.sample(working_data_set, numSubSet)

            mean_min = sum(subset)/len(subset)
            cnt_min = int (round(mean_min, 0))
            if cnt_min in results:
                # raise the occurance of having cnt_sp finalized by the given remaining minutes
                results[cnt_min] += 1
            else:
                # other wise add the result as new entry for this trial
                results[cnt_min] = 1

            for key in results:
                results[key] = results[key]/numSubSet

        return results

    def __get_prediction_minutes_to_finalize(self, mc_results, remaining_storypoints, prediction_map):
        perc50 = perc70 = perc85 = perc95 = 0.0
        sorted_dict = {k:v for k,v in sorted(mc_results.items())}

        mean = sum(sorted_dict.keys()) / len(sorted_dict)
        st_dev = stdev(sorted_dict.keys())

        print("----------------Result----------------")
        print("Estimation of Minutes to finalize {0} Story Points".format(remaining_storypoints))
        print("Mean number of minutes to finalize {0} Story Points: {1} min. => {2} hours".format(remaining_storypoints, round(mean,1), round(mean/60,2)))
        print("Standard deviation of minutes to finalize {0} Story Points: {1}".format(remaining_storypoints, round(st_dev,3)))
        print("Number of trials: {0} and size of subset: {1}".format(self.trials, remaining_storypoints))
        print("----------------Result end------------")

        if self.save_charts:
            plt.figure(figsize=(15, 9))
            when_chart_path = os.path.join(self.charts_folder, 'Minutes_to_finalize_{0}.png'.format(remaining_storypoints))
            print("Storing Chart at {0}".format(when_chart_path))


            plt.bar(list(sorted_dict.keys()), sorted_dict.values(), width = 0.8, color='g')
            plt.xlabel("Minutes to finalize")
            plt.ylabel("Possibility of occurance within {0} number of trials".format(self.trials))
            plt.title("Minutes Trials to finalize {0} Story Point".format(remaining_storypoints))


            self.add_timestamp(plt)
            plt.savefig(when_chart_path)

        prediction = Prediction(remaining_storypoints, st_dev, mean, perc50, perc70, perc85, perc95)
        if prediction_map:
            prediction_map.add(prediction)
        else:
            prediction_map = pd.DataFrame.from_dict(prediction.to_dict(), orient='index')
        return prediction_map

########################### SIM How Many Story Points ####################################
    def how_many_storypoints(self, remaining_minutes):
        target_hours = remaining_minutes / 60
        print("--------------------------------")
        print("Running Monte Carlo Simulation 2 - Predict the number of StoryPoint finished in {0} Hours".format(target_hours))
        print("--------------------------------")
        #### berechnung findet auf minuten basis statt

        mc_result = self.__run_mc_storypoints_per_timespan(remaining_minutes)
        print ("######Validity Check of MC result not yet implemented.###")


        mean_storypoint_estimations, std_dev_storypoint_estimation = self.__get_prediction_storypoints_per_timespan(mc_result,target_hours,remaining_minutes)
        return mean_storypoint_estimations, std_dev_storypoint_estimation

    #Try several times to randomly choose a subsample of size remaining minutes and sum up the number of finished story points
    def __run_mc_storypoints_per_timespan(self, remaining_minutes):
        #total_sp rounded to 2 digit -> cntOccourance
        results = {}

        #try for several times to minimize the possibility of bad luck
        for i in range(self.trials):

            #randomize the entries of self.storypoints_per_minute
            #rand_sp_per_min = self.__prepare_random_sorting_of()

            working_data_set = self.storypoints_per_minute.copy()

            while len(working_data_set) < remaining_minutes:
                working_data_set.extend(self.storypoints_per_minute)

            subset = random.sample(working_data_set, remaining_minutes)

            finished_sp = sum(subset)

            cnt_sp = round(finished_sp, 2)
            if cnt_sp in results:
                # raise the occurance of having cnt_sp finalized by the given remaining minutes
                results[cnt_sp] += 1
            else:
                # other wise add the result as new entry for this trial
                results[cnt_sp] = 1
        return results

    def __get_prediction_storypoints_per_timespan(self, mc_results, working_hours, subsetSize):
        sorted_dict = {k:v for k,v in sorted(mc_results.items())}

        mean_storypoint_estimations = sum(sorted_dict.keys()) / len(sorted_dict)
        std_dev_storypoint_estimation = stdev(sorted_dict.keys())

        print("----------------Result----------------")
        print("Estimation of storypoints per {0} hours".format(working_hours))
        print("Mean number of storypoints within {0} hours: {1}".format(working_hours, round(mean_storypoint_estimations,3)))
        print("Standard deviation of storypoints within {0} hours: {1}".format(working_hours, round(std_dev_storypoint_estimation,3)))
        print("Number of trials: {0} and size of subset: {1}".format(self.trials, subsetSize))
        print("----------------Result end------------")

        if self.save_charts:
            plt.figure(figsize=(15, 9))
            when_chart_path = os.path.join(self.charts_folder, 'storypoints_per_remaining_hours_{0}.png'.format(working_hours))
            print("Storing Chart at {0}".format(when_chart_path))


            plt.bar(list(sorted_dict.keys()), sorted_dict.values(), width = 0.8, color='g')
            plt.xlabel("Story Points finished")
            plt.ylabel("Possibility of occurance within {0} number of trials".format(self.trials))
            plt.title("Story Point Prediction for {0} working hours".format(working_hours))


            self.add_timestamp(plt)
            plt.savefig(when_chart_path)
        return mean_storypoint_estimations, std_dev_storypoint_estimation

    def add_timestamp(self, plt):
        plt.text(1, 1.02, f"Generated on {date.today().strftime("%d.%m.%Y %H:%M")}", transform=plt.gca().transAxes, fontsize=10, ha='right', va='top')
