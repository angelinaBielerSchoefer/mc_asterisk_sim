from datetime import  datetime
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor

from matplotlib import pyplot as plt
from statistics import stdev, mean
from actor import Actor
from playground import Playground


class Game:
    def __init__(self,
                 num_trials,
                 num_actors,
                 assume,
                 parallel = True,
                 save_charts = True,
                 start_year = 2008,
                 target_year = 2030,
                 ):
        self.num_trials = num_trials
        self.num_actors = num_actors

        self.assume = assume
        self.parallel = parallel
        self.save_charts = save_charts
        self.start_year = start_year
        self.target_year = target_year

        self.charts_folder = os.path.join(os.getcwd(), 'Charts_SIM5')
        self.start_time = datetime.now()
        self.current_date = self.start_time.strftime('%Y%m%d_%H%M')
        self.current_year = int(datetime.now().strftime('%Y'))
        self.current_month = int(datetime.now().strftime('%m'))

    def start_simulation(self, data):
        self.data = data
        self.sc1  = {}
        self.sc2  = {}
        print("----- Execution of Scenario 1 -----")
        if self.parallel:
            print("Implementation ongoing")
            self.sc1 = self.__run_simulation_one_parallel()
        else:
            for i in range(self.num_trials):
                self.sc1[i] = self.simulate_one_trial_of_scenario_one(i)
        print("----- Execution of Scenario 2 -----")
        if self.parallel:
            print("not yet implemented")
            self.sc2 = self.__run_simulation_two_parallel()
        else:
            for i in range(self.num_trials):
                self.sc2[i] = self.simulate_one_trial_of_scenario_two(i)
        return self.sc1, self.sc2

    def __run_simulation_one_parallel(self):
        with ProcessPoolExecutor() as executor:
            keys = list(range(self.num_trials))
            result = executor.map(self.simulate_one_trial_of_scenario_one, keys)
            mc_result = dict(zip(keys, result))

        return mc_result
    def __run_simulation_two_parallel(self):
        with ProcessPoolExecutor() as executor:
            keys = list(range(self.num_trials))
            result = executor.map(self.simulate_one_trial_of_scenario_two, keys)
            mc_result = dict(zip(keys, result))

        return mc_result

    def simulate_one_trial_of_scenario_one(self, trial_cnt):
        business_power_pi = [1.2, -0.7, 0.34]
        market_condition_pi = [0.7, -0.9, 2.3]
        market = Playground(self.assume,business_power_pi,market_condition_pi)
        list_actors = []
        for i in range(self.num_actors):
            business_capital, business_value, delta_business_value = market.sim_start_of_company(self.num_actors)
            company =  Actor(business_capital, business_value)
            list_actors.append(company)
        year = self.start_year
        gdp_years = []
        while year >= self.target_year:
            gdp = 0
            capital_sum = 0
            for company in list_actors:
                business_capital = company.calc_business_capital()
                business_value = company.calc_business_value()

                capital_sum += business_capital
                gdp += business_value
            gdp_years.append(gdp_years)
            year += 1
        return gdp_years
    def simulate_one_trial_of_scenario_two(self, trial_cnt):
        return










    def plot_results(self, data, sc1_result, sc2_result, csv_service):
        # tuple
        # [0] = name of plot file and title
        # [1] = unit
        # [2] = data
        # [3] = results of sc1
        # [4] = results of sc2

        plot_labels = [
            ('gdp', 'mil euro', data, sc1_result, sc2_result)

        ]
        self.csv_service = csv_service
        #self.transform_data_and_plot(
        #    ('co2_market', 'Co2_Emission_sum', 'co2_emission_sum', 'co2_emission_sum','mio metric tones Co2 Emission')
        #)
        plot_time_start = datetime.now()
        with ProcessPoolExecutor() as executor:
            keys = plot_labels
            executor.map(self.transform_data_and_plot, keys)

        plot_time_end = datetime.now()
        delta_time = plot_time_end-plot_time_start
        print("Time to generat plots: {0}".format(delta_time))
        return

    def transform_data_and_plot(self, tuple):
        self.end_time = datetime.now()

        # tuple
        # [0] = name of plot file and title
        # [1] = unit
        # [2] = data
        # [3] = results of sc1
        # [4] = results of sc2

        plot_name = tuple[0]
        unit = tuple[1]
        data = tuple[2] #plot_label[0]
        scen1 = tuple[3] #plot_label[1]
        scen2 = tuple[4] #plot_label[1]
        #            if not year in data[scenario]:
        #                    data[scenario][year] = {}
        #                if not year in trial_list:
        #                    trial_list[year] = []
        #                trial_list[year].append(mc_result[scenario][cnt][market].journal[year][sce_label])
        #                mean_v = mean(trial_list[year])
        #                min_v = np.percentile(trial_list[year], 2.5, axis=0)  # lower 2.5%
        #                max_v = np.percentile(trial_list[year], 97.5, axis=0)  # upper 97.5%
        #                data[scenario][year]['min'] = min_v
        #                data[scenario][year]['mean'] = mean_v
        #                data[scenario][year]['max'] = max_v
        #                year+= 1
        print("tupel: {0}".format(tuple))

        sc1_min = []
        sc1_mean = []
        sc1_max = []
        sc2_min = []
        sc2_mean = []
        sc2_max = []
        for year in range(self.start_year, self.target_year+1):
            position = self.start_year - year
            result_list_in_year = []
            for trial_i in scen1:
                result_list_in_year.append(trial_i[position])
            sc1_min.append(min(result_list_in_year))
            sc1_mean.append(mean(result_list_in_year))
            sc1_max.append(max(result_list_in_year))

            for trial_i in scen2:
                result_list_in_year.append(trial_i[position])
            sc2_min.append(min(result_list_in_year))
            sc2_mean.append(mean(result_list_in_year))
            sc2_max.append(max(result_list_in_year))

        self.__plot_mc_results(data,
                               sc1_min,
                               sc1_mean,
                               sc1_max,
                               sc2_min,
                               sc2_mean,
                               sc2_max,
                               plot_name, unit)
        #self.csv_service.save_mc_result_sim4(data, tuple, self.start_year, self.target_year, self.end_time.strftime('%Y%m%d_%H%M'))

    def __plot_mc_results(self, data,
                                sc1_min,
                                sc1_mean,
                                sc1_max,
                                sc2_min,
                                sc2_mean,
                                sc2_max,
                              name,
                              unit ):
        if self.save_charts:
            tp_run_chart_path = os.path.join(self.charts_folder, '{0}_{1}.png'.format(self.end_time.strftime('%Y%m%d_%H%M'),name))
            plt.figure(figsize=(15, 9))

            color_code = {}
            color_code['data'] = 'red'
            color_code['sc1'] = 'black'
            color_code['sc2'] = 'blue'
            color_code['sc3'] = 'green'


            print("Storing Chart at {0}".format(tp_run_chart_path))
            plt.title("{0} {1}".format(name, unit))

            x = list(range(self.start_year, self.target_year+1))

            plt.plot(x, data, color_code['data'], linestyle='-',label="data")
            plt.plot(x, sc1_mean, color_code['sc1'], linestyle='-',label="scenario 1")
            plt.plot(x, sc2_mean, color_code['sc2'], linestyle='-',label="scenario 2")
            plt.fill_between(x, sc1_min, sc1_max, color=color_code['sc1'], alpha=0.2, label='95% confidence interval sc1')
            plt.fill_between(x, sc2_min, sc2_max, color=color_code['sc2'], alpha=0.2, label='95% confidence interval sc2')

            plt.legend()


            #confi_interval = (min_2020, max_2020)
            self.add_timestamp(plt)#,confi_interval)
            plt.savefig(tp_run_chart_path)
        return
    def add_timestamp(self, plt, confidence_interval = (0.0, 0.0)):
        plt.text(1, 1.02, f"Generated on {self.current_date}", transform=plt.gca().transAxes, fontsize=10, ha='right', va='top')


        note_text = ("Number of companies: {0}\n"
                     "Number of trials:{1}\n"
#                     "stdev business power: {2}\n"
#                     "stdev market_influence: {3}\n"
#                     "stdev start value gdp: {4}\n"
#                     "stdev start value Total Assets: {5}\n"
        .format(
            self.num_actors,
            self.num_trials,
#            self.assume['stdev_business_power'],
#            self.assume['stdev_market_influence'],
#            (self.assume['stdev_start_value']/self.num_actors),
#            (self.assume['stdev_start_assets']/self.num_actors),
        ))

        if not (confidence_interval[0] == 0.0 and confidence_interval[1] == 0.0):
            note_text = ("{0}"
                         "sc1: confidence interval (2020): {1}\n").format(note_text, confidence_interval)

        plt.text(0.1, 0.9, note_text, transform=plt.gca().transAxes,fontsize=10, va='top', ha='left', color='blue')

