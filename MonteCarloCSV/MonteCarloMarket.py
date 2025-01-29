import math
import sys

import numpy as np
import os
import random

from collections import Counter
from Company import Company
from concurrent.futures import ProcessPoolExecutor
from datetime import date, datetime, timedelta
from statistics import stdev, mean
from MarketCo2 import MarketCo2
from MarketGeneral import MarketGeneral
import matplotlib.pyplot as plt
from scipy.stats import norm


class MonteCarloMarket:

    def __init__(self,

                 #Test setup 1: trials 1000 num_com 50
                 #Test setup 2: trials 10000 num_com 5
                 ## run time about 4:30
                 market_trials,
                 #Ziel 10.000 Trials
                 number_companies, #000,
                 #Ziel 500.000 Großunternehmen in Deutschland
                 assume ={},
                 parallel = True,
                 save_charts = True,
                 start_year = 2008
                 ):
        self.assume = assume
        self.number_companies = number_companies
        self.parallel = parallel
        self.save_charts = save_charts
        self.start_year = start_year
        self.trials_market = market_trials

        self.charts_folder = os.path.join(os.getcwd(), 'Charts_SIM4_market')
        self.start_time = datetime.now()
        self.current_date = self.start_time.strftime('%Y%m%d_%H%M')
        self.current_year = int(datetime.now().strftime('%Y'))
        self.current_month = int(datetime.now().strftime('%m'))

        script_dir = os.path.dirname(os.path.abspath(__file__))

    def start_simulation(self,
                         data_atmosphere_year_value,
                         data_bvbig_year_value,
                         data_capbig_year_value,
                         data_co2_free_allowances_value,
                         data_co2_price_year_value,
                         data_co2_sold_allowances_value,
                         data_emissions_year_value,
                         data_gdp_year_value,
                         data_investment_by_category_year_value,
                         data_total_assets_year_value,
                         target_year,
                         target_pb,
                         ):

        #self.__size_recalc()
        if (target_pb!="atmosphere"): return 0,0;
        mc_result = {}

        mc_result['data']={}
        #gdp in Billion US Dollar
        mc_result['data']['assume'] = self.assume #predefined assumptions
        mc_result['data']['business_values'] = data_bvbig_year_value# in million euro
        mc_result['data']['capitals'] = data_capbig_year_value# in million euro
        mc_result['data']['verified_co2_emission'] = data_emissions_year_value # metric tone
        mc_result['data']['co2_price'] = data_co2_price_year_value# UNIT???
        mc_result['data']['company_category'] = data_investment_by_category_year_value# million eur per staff-size???
        mc_result['data']['gdp'] = data_gdp_year_value # in million euro
        mc_result['data']['free_allowances'] = data_co2_free_allowances_value #metric tone
        mc_result['data']['sold_allowances'] = data_co2_sold_allowances_value #metric tone
        mc_result['data']['state_of_atmosphere'] = data_atmosphere_year_value # 420ppm in 2022
        mc_result['data']['total_assets'] = data_total_assets_year_value #unit??


        print("----- Execution of Data calculation-----")
        mc_result['data'] = self.__prerun_data_input(mc_result['data'])
        self.mc_data = mc_result['data']
        print("----- Execution of Scenario 1 -----")

        if self.parallel:
            print("Implementation ongoing")
            mc_result['sc1'] = self.__run_simulation_competitive_pricing_parallel()
        else:
            print("skipped")
            #mc_result['sc1'] = self.__run_simulation_competitive_pricing( target_year+3, mc_result['data'])

        print("----- Execution of Scenario 2 -----")
        print("not yet Implemented")
        #mc_result['sc2'] = self.__run_simulation_scenario_two(sim_start, target_year+3,mc_result['sc1'])

        print("----- Execution of Scenario 3 -----")
        print("not yet Implemented")
        #mc_result['sc3']=self.__run_simulation_scenario_three(sim_start, target_year+3,mc_result['sc2'])


        sig_result = {}
        print("----- Significance analysis 1: Validation of Success Model (Data to Sc1) -----")
        print("not yet Implemented")
        #sig_result['val_suc_model'] = self.__validate_success_model(sim_start-1, mc_result['data'], mc_result['sc1'])

        print("----- Significance analysis 2: Validation of ecoPerformance Model (Sc1 to Sc2) -----")
        print("not yet Implemented")
        #sig_result['val_eco_model'] = self.__validate_eco_model(sim_start-1, mc_result['sc1'],mc_result['sc2'])


        #print("----- Significance analysis 3: Validate success optimization (Sc2 to Sc3) -----")
        #print("not yet Implemented")
        #sig_result['proof_impact'] = self.__evaluate_treatment_effect(target_year, mc_result['sc2'],mc_result['sc3'])

        self.end_time = datetime.now()
        time_needed_to_execute = self.end_time- self.start_time
        print("Time to execute: {0}".format(time_needed_to_execute))

        return mc_result, sig_result



    def __evaluate_treatment_effect(self, target_year, mc_result_sc2, mc_result_sc3):
        proof_impact = {}
        year = target_year

        proof_impact[year] = {}
        proof_impact[year]['H0_eco'] = "mu_eco_sc2 != mu_eco_sc3"
        proof_impact[year]['H1_eco'] = "mu_eco_sc2 = mu_eco_sc3"
        proof_impact[year]['expected_eco'] = "large significant difference"
        proof_impact[year]['test_variable_eco'] = test_var_eco = "state_of_atmosphere"

        testlevel_alpha = 0.05 #produzentenrisiko_alpha #meint alpha = 0,05 = prob(X_420<=x_krit)
        effect_size_delta = 0.8 #large effect
        teststrength_beta = 0.1 #Fehlerquote 2. Art
        stichprobenumfang_n = self.__get_optimal_sample_size(effect_size_delta,teststrength_beta,testlevel_alpha)

        mu_eco_sc2 = mean(mc_result_sc2[test_var_eco][year])
        mu_eco_sc3 = mean(mc_result_sc3[test_var_eco][year])
        sigma_eco_sc2 = stdev(mc_result_sc2[test_var_eco][year])
        sigma_eco_sc3 = stdev(mc_result_sc3[test_var_eco][year])

        proof_impact[year]['mu_eco_sc2'] = mu_eco_sc2
        proof_impact[year]['mu_eco_sc3'] = mu_eco_sc3
        proof_impact[year]['sigma_eco_sc2'] = sigma_eco_sc2
        proof_impact[year]['sigma_eco_sc3'] = sigma_eco_sc3

        sample_eco_sc2 = random.sample(mc_result_sc2[test_var_eco][year], stichprobenumfang_n)
        sample_eco_sc3 = random.sample(mc_result_sc3[test_var_eco][year], stichprobenumfang_n)

        x_bar_eco_sc2 = mean(sample_eco_sc2)
        x_bar_eco_sc3 = mean(sample_eco_sc3)

        z_eco_test = ((x_bar_eco_sc2 -x_bar_eco_sc3) - (mu_eco_sc2-mu_eco_sc3)) / ((sigma_eco_sc2**2/stichprobenumfang_n + sigma_eco_sc3**2/stichprobenumfang_n)**0.5)

        print("mu eco sc2: {0}".format(mu_eco_sc2))
        print("mu eco sc3: {0}".format(mu_eco_sc3))

        print("x_bar eco sc2: {0}".format(x_bar_eco_sc2))
        print("x_bar eco sc3: {0}".format(x_bar_eco_sc3))

        print("sigma eco sc2: {0}".format(sigma_eco_sc2))
        print("sigma eco sc2: {0}".format(sigma_eco_sc3))

        print("n large effect: {0}".format(stichprobenumfang_n))


        z_between_min_max = norm.ppf(1 - testlevel_alpha / 2)
        proof_impact[year]['z_eco_test'] = z_eco_test
        proof_impact[year]['z_between_min_max'] = z_between_min_max
        if abs(z_eco_test) > z_between_min_max:
            proof_impact[year]['accept_H0_eco'] = True
            proof_impact[year]['accept_H1_eco'] = False
        else:
            proof_impact[year]['accept_H0_eco'] = False
            proof_impact[year]['accept_H1_eco'] = True
        proof_impact[year]['state_of_atmosphere'] = mu_eco_sc3


        mu_suc_0 = 0
        x_suc_bar = 0
        streuung_sigma = 0
        proof_impact[year]['mu_suc_sc2'] = mu_suc_0
        proof_impact[year]['mu_suc_sc3'] = x_suc_bar
        proof_impact[year]['sigma_suc_sc2'] = 0
        proof_impact[year]['sigma_suc_sc3'] = streuung_sigma
        proof_impact[year]['H0_suc'] = "mu_suc_data = mu_suc_sc1"
        proof_impact[year]['H1_suc'] = "mu_suc_data != mu_suc_sc1"
        proof_impact[year]['expected_suc'] = "small significant difference"




        return proof_impact

    def __validate_eco_model(self, target_year,mc_result_sc1, mc_result_sc2):
        year = target_year
