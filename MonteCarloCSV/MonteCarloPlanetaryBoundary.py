import random
import math
import numpy as np
from datetime import date, datetime, timedelta
from statistics import stdev, mean
#from math import sqrt

from numpy.ma.core import minimum
from scipy.stats import norm

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from contourpy.util.data import simple
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import pandas as pd

import os

from pandas import DataFrame


class MonteCarloPlanetaryBoundary:




    def __init__(self, save_charts = False, trials=100):
        self.trials = trials
        self.rel_gdp2cap = 0
        self.save_charts = save_charts
        self.charts_folder = os.path.join(os.getcwd(), 'Charts_SIM3_PB_testing')

        self.current_date = datetime.now().strftime('%Y%m%d_%H%M')
        self.current_year = int(datetime.now().strftime('%Y'))
        self.current_month = int(datetime.now().strftime('%m'))
        script_dir = os.path.dirname(os.path.abspath(__file__))
    def start_simulation_in_three_scenarios(self,sim_start, target_year,target_pb,
                                            data_gdp_year_value                                            ,
                                            data_total_assets_year_value,
                                            data_atmosphere_year_value,
                                            data_emissions_year_value,
                                            data_co2_price_year_value):
        if (target_pb!="atmosphere"): return 0,0;
        mc_result = {}

        mc_result['data']={}
        #gdp in Billion US Dollar
        mc_result['data']['gdp'] = data_gdp_year_value
        mc_result['data']['total_assets'] = data_total_assets_year_value #recalculated to billion us dollar while read
        mc_result['data']['co2_emission'] = data_emissions_year_value #37,15 GigaTonnen in 2022
        mc_result['data']['state_of_atmosphere'] = data_atmosphere_year_value # 420ppm in 2022
        mc_result['data']['co2_price'] = data_co2_price_year_value# us dollar pro tonne co2 emission

        print("----- Execution of Data calculation-----")
        mc_result['data'] = self.__prerun_data_input(sim_start, target_year+3,mc_result['data'])

        print("----- Execution of Scenario 1 -----")
        mc_result['sc1'] = self.__run_simulation_scenario_one(sim_start, target_year+3, mc_result['data'])




        print("----- Execution of Scenario 2 -----")
        mc_result['sc2'] = self.__run_simulation_scenario_two(sim_start, target_year+3,mc_result['sc1'])

        #self.__format_validation(mc_result['sc1']['co2_price'], "co2_price sc1")
        #self.__format_validation(mc_result['sc2']['co2_price'], "co2_price sc2")


        print("----- Execution of Scenario 3 -----")
        mc_result['sc3']=self.__run_simulation_scenario_three(sim_start, target_year+3,mc_result['sc2'])


        sig_result = {}
        print("----- Significance analysis 1: Validation of Success Model (Data to Sc1) -----")
        print(" Ongoing implementation")
        sig_result['val_suc_model'] = self.__validate_success_model(sim_start-1, mc_result['data'], mc_result['sc1'])

        print("----- Significance analysis 2: Validation of ecoPerformance Model (Sc1 to Sc2) -----")
        print("ongoing implementation")
        sig_result['val_eco_model'] = self.__validate_eco_model(sim_start-1, mc_result['sc1'],mc_result['sc2'])


        print("----- Significance analysis 3: Validate success optimization (Sc2 to Sc3) -----")
        print("not yet Implemented")
        sig_result['proof_impact'] = self.__evaluate_treatment_effect(target_year, mc_result['sc2'],mc_result['sc3'])

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

        testlevel_alpha = 0.05 #produzentenrisiko_alpha #meint alpha = 0,05 = prob(X_420<=x_krit)
        effect_size_delta = 0.5 #medium effect
        teststrength_beta = 0.1 #Fehlerquote 2. Art
        stichprobenumfang_n = self.__get_optimal_sample_size(effect_size_delta,teststrength_beta,testlevel_alpha)

        ## Result
        val_eco_model = {}
        val_eco_model[year] = {}

        ## test no significant difference of atmosphere
        mu_eco_0 = mean(mc_result_sc1['state_of_atmosphere'][year])

        ## take a random sample
        sample_to_test = random.sample(mc_result_sc2['state_of_atmosphere'][year], stichprobenumfang_n)
        x_eco_bar = mean(sample_to_test)
        streuung_sigma_eco = stdev(sample_to_test)
        if streuung_sigma_eco==0:
            streuung_sigma_eco += 0.000001
            print("sigma_eco_sc2  adjusted to avoid division by zero")
        #take test values from random sample
        z = (x_eco_bar - mu_eco_0) / (streuung_sigma_eco / (stichprobenumfang_n ** 0.5))
        z_between_min_max = norm.ppf(1 - testlevel_alpha / 2)

        val_eco_model[year]['mu_eco_sc1'] = mu_eco_0
        val_eco_model[year]['mu_eco_sc2'] = x_eco_bar
        val_eco_model[year]['sigma_eco_data'] = 0
        val_eco_model[year]['sigma_eco_sc1'] = streuung_sigma_eco
        val_eco_model[year]['H0_eco'] = "mu_eco_data = mu_eco_sc2"
        val_eco_model[year]['H1_eco'] = "mu_eco_data != mu_eco_sc2"
        val_eco_model[year]['expected_eco'] = "no significant difference in ecological performance"

        val_eco_model[year]['state_of_atmosphere'] = mean(mc_result_sc2['state_of_atmosphere'][year])


        if abs(z) > z_between_min_max:
            val_eco_model[year]['accept_H0_eco'] = False
            val_eco_model[year]['accept_H1_eco'] = True
        else:
            val_eco_model[year]['accept_H0_eco'] = True
            val_eco_model[year]['accept_H1_eco'] = False


        sample_to_test_sc1 = random.sample(mc_result_sc1['success'][year], stichprobenumfang_n)

        sample_to_test_sc2 =random.sample(mc_result_sc2['success'][year], stichprobenumfang_n)
        x_suc_bar_sc1 = mean(sample_to_test_sc1)
        x_suc_bar_sc2 = mean(sample_to_test_sc2)
        sigma_suc_sc1 = stdev(sample_to_test_sc1)
        sigma_suc_sc2 = stdev(sample_to_test_sc2)

        if sigma_suc_sc1 == 0:
            sigma_suc_sc1+= 0.000001
            print("sigma_suc_sc1 adjusted to avoid division by zero")
        if sigma_suc_sc2 == 0:
            sigma_suc_sc2+= 0.000001
            print("sigma_suc_sc2 adjusted to avoid division by zero")

        #Aus der Stichprobe gezogene Testwert
        diff_mu = x_suc_bar_sc1 - x_suc_bar_sc2
        variability_sigma = math.sqrt(sigma_suc_sc1**2/stichprobenumfang_n + sigma_suc_sc2**2/stichprobenumfang_n)
        z = diff_mu/ variability_sigma
        #(x_bar - mu_0) / (streuung_sigma / (stichprobenumfang_n ** 0.5))
        z_between_min_max = norm.ppf(1 - testlevel_alpha / 2)



        val_eco_model[year]['mu_suc_sc1'] = x_suc_bar_sc1
        val_eco_model[year]['mu_suc_sc2'] = x_suc_bar_sc2
        val_eco_model[year]['sigma_suc_sc1'] = sigma_suc_sc1
        val_eco_model[year]['sigma_suc_sc2'] = sigma_suc_sc2

        val_eco_model[year]['H0_suc'] = "mu_suc_sc1 != mu_suc_sc2"
        val_eco_model[year]['H1_suc'] = "mu_suc_sc1 = mu_suc_sc2"
        val_eco_model[year]['expected_suc'] = "a significant difference"

        ## if possibility is outside of min-max-threshold
        if abs(z) > z_between_min_max:
            val_eco_model[year]['accept_H0_suc'] = True
            val_eco_model[year]['accept_H1_suc'] = False
        else:
            val_eco_model[year]['accept_H0_suc'] = False
            val_eco_model[year]['accept_H1_suc'] = True

        return val_eco_model

    def __validate_success_model(self, target_year, mc_data, mc_result_sc1):
        year = target_year
        testlevel_alpha = 0.05 #produzentenrisiko_alpha #meint alpha = 0,05 = prob(X_420<=x_krit)
        effect_size_delta = 0.5 #medium effect
        teststrength_beta = 0.1 #Fehlerquote 2. Art

        mu_0 = mc_data['success'][year]


        stichprobenumfang_n = self.__get_optimal_sample_size(effect_size_delta,teststrength_beta,testlevel_alpha)

        #print("in validate success model variable n: {0}".format(stichprobenumfang_n))


        sample_to_test = random.sample(mc_result_sc1['success'][year], stichprobenumfang_n)

        x_bar = mean(sample_to_test)
        streuung_sigma = stdev(sample_to_test)
        if streuung_sigma == 0:
            streuung_sigma+=0.00000000001
            print("sigma adjusted to avoid devision by zero")

        #Aus der Stichprobe gezogene Testwert
        z = (x_bar - mu_0) / (streuung_sigma / (stichprobenumfang_n ** 0.5))

        z_between_min_max = norm.ppf(1 - testlevel_alpha / 2)

        val_suc_model = {}
        val_suc_model[year] = {}
        val_suc_model[year]['mu_suc_data'] = mu_0
        val_suc_model[year]['mu_suc_sc1'] = x_bar
        val_suc_model[year]['sigma_suc_data'] = 0
        val_suc_model[year]['sigma_suc_sc1'] = streuung_sigma
        val_suc_model[year]['H0_suc'] = "mu_suc_data = mu_suc_sc1"
        val_suc_model[year]['H1_suc'] = "mu_suc_data != mu_suc_sc1"
        val_suc_model[year]['expected'] = "no significant difference"

        if abs(z) > z_between_min_max:
            val_suc_model[year]['accept_H0'] = False
            val_suc_model[year]['accept_H1'] = True
        else:
            val_suc_model[year]['accept_H0'] = True
            val_suc_model[year]['accept_H1'] = False


        return val_suc_model



    def __get_optimal_sample_size(self,effect_size_delta, teststrengh_beta, testlevel_alpha):
        #Notwendig, da bei zugroßen stichproben auch nicht relevante effekte aufgedeckt werden könnten (kae06 S.328)!!!!

        z_beta = norm.ppf(1-teststrengh_beta)
        z_alpha = norm.ppf(testlevel_alpha)
        n = ((z_beta-z_alpha)/effect_size_delta)**2
        n = int(round(n,0))
        return n

    def __get_mu1_by_effect_size(self, mu0, sigma, effect_size_delta):
        mu1 = mu0-effect_size_delta+sigma
        return mu1

    def __get_effect_size(self, mu0, mu1, sigma):
        delta = abs((mu0-mu1)/sigma)
        out = "no effect"
        if delta>= 0.8:
            out = "large effect"
        else:
            if delta >=0.5:
                out = "medium effect"
            else:
                if delta > 0.2:
                    out = "small effect"

        return delta, out

    def __run_simulation_scenario_one(self, start_sim, target_year, mc_data):
        mc_result={}
        ## data from file
        mc_result['co2_consumption'] = mc_data['co2_consumption'] # in giga tonnen
        mc_result['co2_emission'] = mc_data['co2_emission'] #37,15 GigaTonnen in 2022
        mc_result['co2_price'] = mc_data['co2_price'] # us dollar pro tonne co2 emission
        mc_result['state_of_atmosphere'] = mc_data['state_of_atmosphere'] # 420ppm in 2022

        data_total_assets = mc_data['total_assets']

        ## simulate variables
        mc_result['business_power_pi']            = mc_data['business_power_pi']
        mc_result['co2_consumption_pi']           = mc_data['co2_consumption_pi']
        mc_result['co2_price_pi']                 = mc_data['co2_price_pi']
        mc_result['market_conditions_pi']         = mc_data['market_conditions_pi']

        ## calculation base
        mc_result['trials'] = {}

        ## create sim run variables
        market_conditions_t =  mc_data['market_conditions']
        business_power = mc_data['business_power']
        co2_consumption = mc_data['co2_consumption']
        co2_price = mc_data['co2_price']
        delta_co2_emission = mc_data['delta_co2_emission']
        ## create sim run sets
        delta_co2_emission_set = list(mc_data['delta_co2_emission'])

        # create for output

        ## terminate the simulation
        start_year = min(mc_data['delta_capital'].keys())+1

        ## set start values
        atmosphere = {start_year-1: [mc_result['state_of_atmosphere'][start_year-1]]}
        capital_total = {start_year-1: [mc_data['total_assets'][start_year-1]]}
        co2_emission = {start_year-1: [mc_data['co2_emission'][start_year-1]]}
        delta_gdp = {start_year-1:[mc_data['delta_gdp'][start_year-1]]}
        gdp = {start_year-1: [mc_data['gdp'][start_year-1]]}


        ## create dics for output
        capital_business = {}
        capital_nature = {}
        delta_capital = {}
        eco_performance = {}
        success = {}
        weight_business = {}
        weight_nature = {}
        winning_increase ={}


        ## plot the mean
        atmosphere_to_plot = {}
        capital_to_plot = {}
        capital_business_to_plot ={}
        capital_nature_to_plot = {}
        delta_capital_to_plot = {}
        delta_gdp_to_plot = {}
        eco_performance_to_plot = {}
        gdp_to_plot = {}
        success_to_plot = {}


        cnt_trials = 0
        while cnt_trials<self.trials:
            if not cnt_trials in mc_result['trials']:
                mc_result['trials'][cnt_trials] ={}
            year = start_year
            while year <= target_year:
                if not year in mc_result['trials'][cnt_trials]:
                    mc_result['trials'][cnt_trials][year] ={}
                if not year in atmosphere:
                    atmosphere[year] = []
                if not year in business_power:
                    business_power[year] = []
                if not year in capital_business:
                    capital_business[year]=[]
                if not year in capital_nature:
                    capital_nature[year] = []
                if not year in capital_total:
                    capital_total[year] = []
                if not year in co2_consumption:
                    co2_consumption[year] = []
                if not year in co2_emission:
                    co2_emission[year] = []
                if not year in co2_price:
                    co2_price[year] = []
                if not year in delta_capital:
                    delta_capital[year]=[]
                if not year in delta_gdp:
                    delta_gdp[year]=[]
                if not year in delta_co2_emission:
                    delta_co2_emission[year] = []
                if not year in eco_performance:
                    eco_performance[year]=[]
                if not year in market_conditions_t:
                    market_conditions_t[year] = []
                if not year in gdp:
                    gdp[year]=[]
                if not year in success:
                    success[year] = []
                if not year in weight_business:
                    weight_business[year]=[]
                if not year in weight_nature:
                    weight_nature[year]=[]

                if not year in winning_increase:
                    winning_increase[year] = []

                sample_size = 10
                ####### SIMULATION of Base Values
                if year >= start_sim:
                    x = random.randint(0,len(mc_data['delta_co2_emission_pi'])-1)
                    sample = mc_data['delta_co2_emission_pi'][x]

                    delta_co2_emission[year].append(sample)
                    sample = random.sample(mc_data['delta_co2_emission_pi'], sample_size)
                    delta_co2_emission_set[year].append(sample)

                    x = random.randint(0,len(mc_data['business_power_pi'])-1)

                    sample = mc_data['business_power_pi'][x]
                    business_power[year].append(sample)

                    x = random.randint(0,len(mc_data['co2_consumption_pi'])-1)

                    sample = mc_data['co2_consumption_pi'][x]
                    co2_consumption[year].append(sample)

                    x = random.randint(0,len(mc_data['co2_price_pi'])-1)

                    sample = mc_data['co2_price_pi'][x]
                    co2_price[year].append(sample)

                    x = random.randint(0,len(mc_data['market_conditions_pi'])-1)

                    sample = mc_data['market_conditions_pi'][x]
                    market_conditions_t[year].append(sample)


                ##prepare input for further scenarios
                mc_result['trials'][cnt_trials][year]['atmosphere_last_year'] = atmosphere[year-1][-1]
                mc_result['trials'][cnt_trials][year]['business_power_last_year'] = business_power[year-1][-1]
                mc_result['trials'][cnt_trials][year]['capital_total_last_year'] = capital_total[year-1][-1]
                mc_result['trials'][cnt_trials][year]['co2_consumption'] = co2_consumption[year][-1]
                mc_result['trials'][cnt_trials][year]['co2_emission_last_year'] = co2_emission[year-1][-1]
                mc_result['trials'][cnt_trials][year]['co2_price'] = co2_price[year][-1]
                mc_result['trials'][cnt_trials][year]['delta_co2_emission'] = delta_co2_emission[year][-1]
                mc_result['trials'][cnt_trials][year]['delta_co2_emission_set'] =delta_co2_emission_set[year][-1]
                mc_result['trials'][cnt_trials][year]['gdp_last_year'] =gdp[year-1][-1]
                mc_result['trials'][cnt_trials][year]['market_conditions_t'] = market_conditions_t[year][-1]

                atmosphere_sim, capital_business_sim, capital_nature_sim, capital_total_sim, co2_emission_simulated,delta_capital_sim, delta_gdp_sim, eco_performance_sim, gdp_sim, success_sim, weight_business_sim, weight_nature_sim, winning_increase_sim= (
                    self.__simulate_one_year_of_sc1(atmosphere[year-1][-1],
                                                    business_power[year-1][-1],
                                                    capital_total[year-1][-1],
                                                    co2_consumption[year][-1],
                                                    co2_emission[year-1][-1],
                                                    co2_price[year][-1],
                                                    delta_co2_emission[year][-1],
                                                    gdp[year-1][-1],
                                                    market_conditions_t[year][-1]))
                mc_result['trials'][cnt_trials][year]['co2_emission'] = co2_emission_simulated

                atmosphere[year].append(atmosphere_sim)
                capital_business[year].append(capital_business_sim)
                capital_nature[year].append(capital_nature_sim)
                capital_total[year].append(capital_total_sim)
                co2_emission[year].append(co2_emission_simulated)
                delta_capital[year].append(delta_capital_sim)
                delta_gdp[year].append(delta_gdp_sim)
                eco_performance[year].append(eco_performance_sim)
                gdp[year].append(gdp_sim)
                success[year].append(success_sim)
                weight_business[year].append(weight_business_sim)
                weight_nature[year].append(weight_nature_sim)
                winning_increase[year].append(winning_increase_sim)

                atmosphere_to_plot[year] = mean(atmosphere[year])
                capital_to_plot[year] = mean(capital_total[year])
                capital_business_to_plot[year] = mean(capital_business[year])
                capital_nature_to_plot[year] = mean(capital_nature[year])
                delta_capital_to_plot[year] = mean(delta_capital[year])
                delta_gdp_to_plot[year] = mean(delta_gdp[year])
                gdp_to_plot[year] = mean(gdp[year])
                eco_performance_to_plot[year]  = mean(eco_performance[year])
                success_to_plot[year] = mean (success[year])

                year+=1
            cnt_trials+=1

        # simulated, calculated
        mc_result['capital_business'] = capital_business
        mc_result['capital_nature'] = capital_nature
        mc_result['capital_total'] = capital_total
        mc_result['delta_co2_emission'] = delta_co2_emission
        mc_result['delta_capital'] = delta_capital
        mc_result['delta_gdp'] = delta_gdp
        mc_result['eco_performance'] = eco_performance
        mc_result['gdp'] = gdp
        mc_result['state_of_atmosphere'] = atmosphere
        mc_result['success'] = success
        mc_result['weight_business'] = weight_business
        mc_result['weight_nature'] = weight_nature
        mc_result['winning_increase'] = winning_increase

        #given by data, further simulated
        mc_result['business_power'] = business_power
        mc_result['co2_consumption'] = co2_consumption
        mc_result['co2_emission'] = co2_emission
        mc_result['co2_price'] = co2_price
        mc_result['market_conditions'] = market_conditions_t

        mc_result['total_assets'] = data_total_assets

        ## mean to plot
        mc_result['atmosphere_to_plot'] = atmosphere_to_plot
        mc_result['capital_business_to_plot'] = capital_business_to_plot
        mc_result['capital_nature_to_plot'] = capital_nature_to_plot
        mc_result['capital_to_plot'] = capital_to_plot
        mc_result['delta_capital_to_plot'] = delta_capital_to_plot
        mc_result['delta_gdp_to_plot'] = delta_gdp_to_plot
        mc_result['eco_performance_to_plot'] = eco_performance_to_plot
        mc_result['gdp_to_plot'] = gdp_to_plot
        mc_result['success_to_plot'] = success_to_plot

        return mc_result
    def __run_simulation_scenario_two(self, start_year, target_year,mc_data):
        mc_result={}
        ## data from file
        mc_result['co2_consumption'] = mc_data['co2_consumption'] # in giga tonnen
        mc_result['co2_emission'] = mc_data['co2_emission'] #37,15 GigaTonnen in 2022
        mc_result['co2_price'] = mc_data['co2_price'] # us dollar pro tonne co2 emission
        mc_result['state_of_atmosphere'] = mc_data['state_of_atmosphere'] # 420ppm in 2022

        ## calculate results
        mc_result['delta_gdp'] = {}
        mc_result['success_to_plot'] = {}

        ## simulate variables
        co2_consumption = mc_data['co2_consumption']
        co2_emission = mc_data['co2_emission']
        co2_price = mc_data['co2_price']
        business_power = mc_data['business_power']
        market_conditions_t =  mc_data['market_conditions']
        data_total_assets = mc_data['total_assets']

        ## terminate the simulation
        start_year = min(data_total_assets.keys())+2

        ## set start values
        gdp = {start_year-1: [mc_data['gdp'][start_year-1][-1]]}
        capital_total = {start_year-1: [data_total_assets[start_year-1]]}
        delta_gdp = {start_year-1:[mc_data['delta_gdp'][start_year-1][-1]]}
        atmosphere = {start_year-1: [mc_data['state_of_atmosphere'][start_year-1][-1]]}

        ## create dics for output
        capital_business = {}
        capital_nature = {}
        eco_performance = {}
        success = {}
        weight_business = {}
        weight_nature = {}
        winning_increase = {}


        ## plot the mean
        atmosphere_to_plot = {}
        capital_business_to_plot = {}
        capital_nature_to_plot = {}
        delta_gdp_to_plot = {}
        eco_performance_to_plot = {}
        gdp_to_plot = {}
        success_to_plot = {}


        cnt_trials = 0
        while cnt_trials<self.trials:
            year = start_year
            while year < max(market_conditions_t.keys()):
                if not year in atmosphere:
                    atmosphere[year] = []
                if not year in capital_business:
                    capital_business[year]=[]
                if not year in capital_nature:
                    capital_nature[year] = []
                if not year in capital_total:
                    capital_total[year] = []
                if not year in delta_gdp:
                    delta_gdp[year]=[]
                if not year in eco_performance:
                    eco_performance[year]=[]
                if not year in gdp:
                    gdp[year]=[]
                if not year in success:
                    success[year] = []
                if not year in weight_business:
                    weight_business[year]=[]
                if not year in weight_nature:
                    weight_nature[year]=[]
                if not year in winning_increase:
                    winning_increase[year] = []

                input_atmosphere_ly         = mc_data['trials'][cnt_trials][year]['atmosphere_last_year']
                input_business_power_ly     = mc_data['trials'][cnt_trials][year]['business_power_last_year']
                input_capital_total_ly      = mc_data['trials'][cnt_trials][year]['capital_total_last_year']
                input_co2_consumption       = mc_data['trials'][cnt_trials][year]['co2_consumption']
                input_co2_emission          = mc_data['trials'][cnt_trials][year]['co2_emission']
                input_co2_price             = mc_data['trials'][cnt_trials][year]['co2_price']
                input_gdp_ly                = mc_data['trials'][cnt_trials][year]['gdp_last_year']
                input_market_conditions     = mc_data['trials'][cnt_trials][year]['market_conditions_t']

                atmosphere_sim, capital_business_sim, capital_nature_sim, capital_total_sim,delta_gdp_sim, eco_performance_sim, gdp_sim, success_sim, weight_business_sim, weight_nature_sim, winning_increase_sim = (
                    self.__simulate_one_year_of_sc2(input_atmosphere_ly,
                                                    input_business_power_ly,
                                                    input_capital_total_ly,
                                                    input_co2_consumption,
                                                    input_co2_emission,
                                                    input_co2_price,
                                                    input_gdp_ly,
                                                    input_market_conditions))



                atmosphere[year].append(atmosphere_sim)
                capital_business[year].append(capital_business_sim)
                capital_nature[year].append(capital_nature_sim)
                capital_total[year].append(capital_total_sim)
                delta_gdp[year].append(delta_gdp_sim)
                eco_performance[year].append(eco_performance_sim)
                gdp[year].append(gdp_sim)
                success[year].append(success_sim)
                weight_business[year].append(weight_business_sim)
                weight_nature[year].append(weight_nature_sim)
                winning_increase[year].append(winning_increase_sim)

                atmosphere_to_plot[year] = mean(atmosphere[year])
                capital_business_to_plot[year] = mean(capital_business[year])
                capital_nature_to_plot[year] = mean(capital_nature[year])
                gdp_to_plot[year] = mean(gdp[year])
                delta_gdp_to_plot[year] = mean(delta_gdp[year])
                eco_performance_to_plot[year]  = mean(eco_performance[year])
                success_to_plot[year] = mean (success[year])
                year+=1
            cnt_trials+=1



        # input trials:
        mc_result['trials'] = mc_data['trials']
        # simulated
        mc_result['capital_business'] = capital_business
        mc_result['capital_nature'] = capital_nature
        mc_result['capital_total'] = capital_total
        mc_result['delta_gdp'] = delta_gdp
        mc_result['eco_performance'] = eco_performance
        mc_result['gdp'] = gdp
        mc_result['state_of_atmosphere'] = atmosphere
        mc_result['success'] = success
        mc_result['weight_business'] = weight_business
        mc_result['weight_nature'] = weight_nature
        mc_result['winning_increase'] = weight_nature

        #given by data
        mc_result['business_power'] = business_power
        mc_result['market_conditions'] = market_conditions_t
        mc_result['total_assets'] = data_total_assets

        ## mean to plot
        mc_result['capital_business_to_plot'] = capital_business_to_plot
        mc_result['capital_nature_to_plot'] = capital_nature_to_plot
        mc_result['gdp_to_plot'] = gdp_to_plot
        mc_result['delta_gdp_to_plot'] = delta_gdp_to_plot
        mc_result['success_to_plot'] = success_to_plot
        mc_result['atmosphere_to_plot'] = atmosphere_to_plot
        mc_result['eco_performance_to_plot'] = eco_performance_to_plot

        return mc_result

    def __run_simulation_scenario_three(self, sim_start, target_year,mc_data):
        mc_result={}
        ## data from file
        mc_result['co2_consumption'] = mc_data['co2_consumption'] # in giga tonnen
        mc_result['co2_emission'] = mc_data['co2_emission'] #37,15 GigaTonnen in 2022
        mc_result['co2_price'] = mc_data['co2_price'] # us dollar pro tonne co2 emission
        mc_result['state_of_atmosphere'] = mc_data['state_of_atmosphere'] # 420ppm in 2022
        data_total_assets = mc_data['total_assets']

        ## simulate variables
        mc_result['delta_capital'] = {}
        mc_result['trials'] = mc_data['trials']

        ## calculate results
        mc_result['delta_gdp'] = {}
        mc_result['success_to_plot'] = {}

        business_power = mc_data['business_power']
        co2_consumption = mc_data['co2_consumption']
        co2_price = mc_data['co2_price']
        market_conditions_t =  mc_data['market_conditions']

        ## terminate the simulation
        start_year = sim_start-1 #min(data_total_assets.keys())+2

        ## set start values
        gdp = {start_year-1: [mc_data['gdp'][start_year-1][-1]]}
        capital_total = {start_year-1: [data_total_assets[start_year-1]]}
        delta_gdp = {start_year-1:[mc_data['delta_gdp'][start_year-1][-1]]}
        atmosphere = {start_year-1: [mc_data['state_of_atmosphere'][start_year-1][-1]]}

        ## create dics for output
        capital_business = {}
        capital_nature = {}
        co2_emission =  {}
        eco_performance = {}
        success = {}
        weight_business = {}
        weight_nature = {}
        winning_increase = {}


        ## plot the mean
        atmosphere_to_plot = {}
        capital_business_to_plot = {}
        capital_nature_to_plot = {}
        delta_gdp_to_plot = {}
        eco_performance_to_plot = {}
        gdp_to_plot = {}
        success_to_plot = {}


        cnt_trials = 0
        while cnt_trials<self.trials:
            year = start_year
            while year <= target_year: #max(market_conditions_t.keys()):
                if not year in atmosphere:
                    atmosphere[year] = []
                if not year in capital_business:
                    capital_business[year]=[]
                if not year in capital_nature:
                    capital_nature[year] = []
                if not year in capital_total:
                    capital_total[year] = []
                if not year in co2_emission:
                    co2_emission[year] = []
                if not year in delta_gdp:
                    delta_gdp[year]=[]
                if not year in eco_performance:
                    eco_performance[year]=[]
                if not year in gdp:
                    gdp[year]=[]
                if not year in success:
                    success[year] = []
                if not year in weight_business:
                    weight_business[year]=[]
                if not year in weight_nature:
                    weight_nature[year]=[]
                if not year in winning_increase:
                    winning_increase[year] = []


                input_atmosphere_ly         = mc_result['trials'][cnt_trials][year]['atmosphere_last_year']
                input_business_power_ly     = mc_result['trials'][cnt_trials][year]['business_power_last_year']
                input_capital_total_ly      = mc_result['trials'][cnt_trials][year]['capital_total_last_year']
                input_co2_consumption       = mc_result['trials'][cnt_trials][year]['co2_consumption']
                input_co2_price             = mc_result['trials'][cnt_trials][year]['co2_price']
                input_gdp_ly                = mc_result['trials'][cnt_trials][year]['gdp_last_year']
                input_market_conditions     = mc_result['trials'][cnt_trials][year]['market_conditions_t']

                atmosphere_sim, capital_business_sim, capital_nature_sim, capital_total_sim,co2_emission_sim, delta_gdp_sim, eco_performance_sim, gdp_sim, success_sim, weight_business_sim, weight_nature_sim, winning_increase_sim = (
                    self.__simulate_one_year_of_sc3(input_atmosphere_ly,
                                                    input_business_power_ly,
                                                    input_capital_total_ly,
                                                    input_co2_consumption,
                                                    input_co2_price,
                                                    input_gdp_ly,
                                                    input_market_conditions))

                if not year+1 in mc_result['trials'][cnt_trials]:
                    mc_result['trials'][cnt_trials][year+1] = {}
                mc_result['trials'][cnt_trials][year+1]['atmosphere_last_year']     = atmosphere_sim
                mc_result['trials'][cnt_trials][year+1]['capital_total_last_year']  = capital_total_sim
                mc_result['trials'][cnt_trials][year+1]['gdp_last_year']            = gdp_sim

                atmosphere[year].append(atmosphere_sim)
                capital_business[year].append(capital_business_sim)
                capital_nature[year].append(capital_nature_sim)
                capital_total[year].append(capital_total_sim)
                co2_emission[year].append(co2_emission_sim)
                delta_gdp[year].append(delta_gdp_sim)
                eco_performance[year].append(eco_performance_sim)
                gdp[year].append(gdp_sim)
                success[year].append(success_sim)
                weight_business[year].append(weight_business_sim)
                weight_nature[year].append(weight_nature_sim)
                winning_increase[year].append(winning_increase_sim)

                atmosphere_to_plot[year] = mean(atmosphere[year])
                capital_business_to_plot[year] = mean(capital_business[year])
                capital_nature_to_plot[year] = mean(capital_nature[year])
                gdp_to_plot[year] = mean(gdp[year])
                delta_gdp_to_plot[year] = mean(delta_gdp[year])
                eco_performance_to_plot[year]  = mean(eco_performance[year])
                success_to_plot[year] = mean (success[year])
                year+=1
            cnt_trials+=1



        # simulated
        mc_result['capital_business'] = capital_business
        mc_result['capital_nature'] = capital_nature
        mc_result['capital_total'] = capital_total
        mc_result['co2_emission'] = co2_emission
        mc_result['delta_gdp'] = delta_gdp
        mc_result['eco_performance'] = eco_performance
        mc_result['gdp'] = gdp
        mc_result['state_of_atmosphere'] = atmosphere
        mc_result['success'] = success
        mc_result['weight_business'] = weight_business
        mc_result['weight_nature'] = weight_nature
        mc_result['winning_increase'] = weight_nature

        #given by data
        mc_result['business_power'] = business_power
        mc_result['market_conditions'] = market_conditions_t

        ## mean to plot
        mc_result['capital_business_to_plot'] = capital_business_to_plot
        mc_result['capital_nature_to_plot'] = capital_nature_to_plot
        mc_result['gdp_to_plot'] = gdp_to_plot
        mc_result['delta_co2_emission_to_plot'] = delta_gdp_to_plot
        mc_result['delta_gdp_to_plot'] = delta_gdp_to_plot
        mc_result['success_to_plot'] = success_to_plot
        mc_result['atmosphere_to_plot'] = atmosphere_to_plot
        mc_result['eco_performance_to_plot'] = eco_performance_to_plot

        self.__format_validation(mc_result['atmosphere_to_plot'], "Atmosphere changes")


        return mc_result

    def __prerun_data_input(self,sim_start, target_year, data_collection):

        data_collection['business_power']       = {}
        data_collection['capital_business']     = {}
        data_collection['capital_nature']       = {}
        data_collection['co2_consumption']      = {}
        data_collection['delta_capital']        = {}
        data_collection['delta_co2_emission']   = {}
        data_collection['delta_gdp']            = {}
        data_collection['eco_performance']      = {}
        data_collection['market_conditions']    = {}
        data_collection['success']              = {}

        cnt_y = 1980
        while cnt_y < 2024:
            if cnt_y in data_collection['co2_price']:
                data_collection['co2_price'][cnt_y] = [data_collection['co2_price'][cnt_y]]
            if cnt_y in data_collection['gdp'] and (cnt_y-1) in data_collection['gdp']:
                data_collection['delta_gdp'][cnt_y] = data_collection['gdp'][cnt_y] - data_collection['gdp'][cnt_y-1]
            ### calc success
            if cnt_y in data_collection['delta_gdp'] and (cnt_y-1) in data_collection['gdp']:
                data_collection['success'][cnt_y] = data_collection['delta_gdp'][cnt_y]/data_collection['gdp'][cnt_y-1]
            if cnt_y in data_collection['co2_emission'] and cnt_y-1 in data_collection['co2_emission']:
                data_collection['delta_co2_emission'][cnt_y] = [data_collection['co2_emission'][cnt_y] - data_collection['co2_emission'][cnt_y-1]]

            ### calc eco_performance
            if (cnt_y in data_collection['co2_emission']
                    and cnt_y+1 in data_collection['state_of_atmosphere']):
                #https://wiki.bildungsserver.de/klimawandel/index.php/Kohlendioxid-Konzentration
                # 1 ppm CO2 = 7,814 Gt CO2
                # co2_em given in Gt CO2
                r_factor = 7.814
                v_co2 = data_collection['co2_emission'][cnt_y] / r_factor ## change of atmospheric state by human impact in ppm
                atmosphere_last_year = data_collection['state_of_atmosphere'][cnt_y-1]
                data_collection['eco_performance'][cnt_y] =self.__calc_eco_impact_by_parabola(atmosphere_last_year,v_co2)
                calc_new_atmosphere_value = atmosphere_last_year + v_co2 #in ppm
                data_new_atmosphere_value = data_collection['state_of_atmosphere'][cnt_y] # in ppm
                co2_consumption = calc_new_atmosphere_value - data_new_atmosphere_value  #calc diff

                data_collection['co2_consumption'][cnt_y] = [co2_consumption * r_factor] # calc to giga tonns
            cnt_y+=1
            ### calc delta capital
            if cnt_y in data_collection['total_assets'] and cnt_y-1 in data_collection['total_assets']:
                data_collection['delta_capital'][cnt_y] = data_collection['total_assets'][cnt_y] - data_collection['total_assets'][cnt_y-1]
                data_collection['capital_business'][cnt_y] = data_collection['total_assets'][cnt_y]
                data_collection['capital_nature'][cnt_y] = 0.0
        data_collection['business_power']       = self.__calc_business_power(data_collection['gdp'], data_collection['delta_capital'])
        data_collection['market_conditions']    = self.__calc_market_conditions(data_collection['delta_gdp'], data_collection['total_assets'])
        #Create simulation base
        data_collection['business_power_pi']            = self.__create_sim_base(data_collection['business_power'])
        data_collection['co2_consumption_pi']           = self.__create_sim_base(data_collection['co2_consumption'])
        data_collection['delta_co2_emission_pi']        = self.__create_sim_base(data_collection['delta_co2_emission'])
        data_collection['co2_price_pi']                 = self.__create_sim_base(data_collection['co2_price'])
        data_collection['market_conditions_pi']         = self.__create_sim_base(data_collection['market_conditions'])



        return data_collection


    def __calc_eco_performance(self, co2_em, co2_consum, state_of_atmosphere_last_year):
        #https://wiki.bildungsserver.de/klimawandel/index.php/Kohlendioxid-Konzentration
        #  1 ppm CO2 = 7,814 Gt CO2
        # co2_em and co2_consumption given in Gt CO2
        r_factor = 7.814

        v_co2 = co2_em / r_factor ## change of atmospheric state by human impact in ppm
        c_co2 = co2_consum / r_factor
        atmosphere_this_year = state_of_atmosphere_last_year + v_co2 - c_co2
        return self.__calc_eco_impact_by_parabola(state_of_atmosphere_last_year,v_co2), atmosphere_this_year

    def __calc_eco_impact_by_parabola(self, state_of_atmosphere, change_co2, optimum=280, threshold=350):
        ## Source master project paper
        x1 = threshold
        x2 = optimum
        x3 = x2 - (x1-x2)
        term = (x1**2-x3**2) / (x3-x1)
        self.a = 1 / ((x2*(x2+term))-(x3*(x3+term)))
        self.b = self.a * term
        self.c = -self.a*x3**2 - self.a*x3*term
        #print ("{0}*x² + {1}*x + {2}".format(a,b,c))
        f_of_state = self.a * state_of_atmosphere**2 + self.b * state_of_atmosphere + self.c
        f_of_change = self.a * (state_of_atmosphere+change_co2)**2 + self.b * (state_of_atmosphere + change_co2) + self.c

        return f_of_change - f_of_state

    def __simulate_one_year_of_sc1(self,
                                   atmosphere_last_year,
                                   business_power_last_year,
                                   capital_last_year,
                                   co2_consum,
                                   co2_emission_last_year,
                                   co2_price,
                                   delta_co2_emission,
                                   gdp_last_year,
                                   market_condition
                                   ):

        delta_capital = (gdp_last_year *business_power_last_year)
        capital_total =  delta_capital + capital_last_year
        co2_emission = co2_emission_last_year + delta_co2_emission
        capital_nature = co2_emission * co2_price
        weight_nature = capital_nature / capital_total
        weight_business = 1 #-weight_nature

        capital_business = capital_total*weight_business

        delta_gdp_sim = capital_business * market_condition
        gdp = gdp_last_year + delta_gdp_sim

        winning_increase = (gdp - gdp_last_year) / gdp_last_year
        eco_performance, atmosphere = self.__calc_eco_performance(co2_emission,co2_consum, atmosphere_last_year)

        success = winning_increase
        return (atmosphere,
                capital_business,
                capital_nature,
                capital_total,
                co2_emission,
                delta_capital,
                delta_gdp_sim,
                eco_performance,
                gdp,
                success,
                weight_business,
                weight_nature,
                winning_increase)

    def __simulate_one_year_of_sc2(self,
                                   atmosphere_last_year,
                                   business_power_last_year,
                                   capital_last_year,
                                   co2_consum,
                                   co2_emission,
                                   co2_price,
                                   gdp_last_year,
                                   market_condition
                                   ):

        delta_capital = (gdp_last_year * business_power_last_year)
        capital_total =  delta_capital + capital_last_year

        weight_business = 1
        capital_business = capital_total*weight_business

        delta_gdp = capital_business * market_condition
        gdp = gdp_last_year + delta_gdp

        winning_increase = (gdp - gdp_last_year) / gdp_last_year
        eco_performance, atmosphere = self.__calc_eco_performance(co2_emission, co2_consum, atmosphere_last_year)

        ####
        success = winning_increase + eco_performance

        capital_nature = co2_emission * co2_price
        weight_nature = capital_nature / capital_total

        return (atmosphere,
                capital_business,
                capital_nature,
                capital_total,
                delta_gdp,
                eco_performance,
                gdp,
                success,
                weight_business,
                weight_nature,
                winning_increase)

    def __simulate_one_year_of_sc3(self,
                                   atmosphere_last_year,
                                   business_power_last_year,
                                   capital_last_year,
                                   co2_consum,
                                   co2_price,
                                   gdp_last_year,
                                   market_condition
                                   ):


        delta_capital = (gdp_last_year *business_power_last_year)
        capital_total =  delta_capital + capital_last_year
        #capital_total =  delta_gdp_last_year /self.rel_gdp2cap + capital_last_year
        weight_nature = self.__optimize_weight_nature(co2_price,
                                                      capital_total,
                                                      gdp_last_year,
                                                      market_condition)
        #new calculated

        weight_business = 1 - weight_nature
        capital_nature = capital_total*weight_nature #co2_emission * co2_price
        capital_business = capital_total*weight_business
        co2_emission = capital_nature/co2_price

        delta_gdp = capital_business * market_condition
        gdp = gdp_last_year + delta_gdp

        winning_increase = (gdp - gdp_last_year) / gdp_last_year
        eco_performance, atmosphere = self.__calc_eco_performance(co2_emission, co2_consum, atmosphere_last_year)

        ####
        success = winning_increase + eco_performance


        return (atmosphere,
                capital_business,
                capital_nature,
                capital_total,
                co2_emission,
                delta_gdp,
                eco_performance,
                gdp,
                success,
                weight_business,
                weight_nature,
                winning_increase)



    def __optimize_weight_nature(self,
                                 co2_price,
                                 capital_total,
                                 gdp_last_year,
                                 market_condition,
                                 ):
        mk_p = market_condition*co2_price
        cap_gdp = 2* gdp_last_year*capital_total*self.a

        term_1 = mk_p / cap_gdp
        term_2 = self.b / (2* self.a * capital_total)

        return term_1-term_2
    def __create_sim_base(self, data_to_sim):
        pi = []
        for key in data_to_sim:
            if len(data_to_sim[key])>0:
                pi.append(data_to_sim[key][-1])
        return pi
    def __calc_business_power(self, data_gdp, data_delta_capital):
        bus_pow = {}

        for year in data_delta_capital:
            if not year in bus_pow:
                bus_pow[year] = []
            if year-1 in data_gdp:
                if not year-1 in bus_pow:
                    bus_pow[year-1] = []
                if data_gdp[year-1] == 0:
                    bus_pow[year-1].append(0)
                else:
                    bus_pow[year-1].append(data_delta_capital[year]/data_gdp[year-1])
        return bus_pow

    def __calc_market_conditions(self,data_delta_gdp,data_total_assets):
        m_cond = {}
        for year in data_delta_gdp:
            if year in data_total_assets:
                if not year in m_cond:
                    m_cond[year] = []
                m_cond[year].append(data_delta_gdp[year] / data_total_assets[year])
        return m_cond

    def plot_mc_results(self, data_to_plot, name="default", type="line"):
        if self.save_charts:
            tp_run_chart_path = os.path.join(self.charts_folder, '{0}_{1}.png'.format(self.current_date,name))
            plt.figure(figsize=(15, 9))

            color_code = {}
            color_code['data'] = 'red'
            color_code['sc1'] = 'black'
            color_code['sc2'] = 'blue'
            color_code['sc3'] = 'green'


            print("Storing Chart at {0}".format(tp_run_chart_path))
            plt.title(name)
            offset = -0.4
            for scenario in data_to_plot:
                if type == "line":
                    plt.plot(list(data_to_plot[scenario].keys()), list(data_to_plot[scenario].values()), color=color_code[scenario], linestyle='-',label=scenario)
                if type == "bar":
                    plt.bar([xi + offset for xi in data_to_plot[scenario].keys()],
                            list(data_to_plot[scenario].values()),
                            width=0.2,

                            color=color_code[scenario],
                            linestyle='-',
                            label=scenario)
                    offset+= 0.2
            plt.legend()
            self.add_timestamp(plt)
            plt.savefig(tp_run_chart_path)
        return

    def plot_capital_weight(self, data_to_plot, name="default"):
        if self.save_charts:
            tp_run_chart_path = os.path.join(self.charts_folder, '{0}_{1}.png'.format(self.current_date,name))
            plt.figure(figsize=(15, 9))

            color_code = {}
            color_code['data'] = {}
            color_code['data']['business'] = 'red'
            color_code['data']['nature'] = 'pink'
            color_code['sc1'] = {}
            color_code['sc1']['business'] = 'black'
            color_code['sc1']['nature'] = 'gray'
            color_code['sc2'] = {}
            color_code['sc2']['business'] = 'blue'
            color_code['sc2']['nature'] = 'lightblue'
            color_code['sc3'] = {}
            color_code['sc3']['business'] = 'green'
            color_code['sc3']['nature'] = 'lightgreen'

            bar_width = 0.1
            bottoms = 0
            print("Storing Chart at {0}".format(tp_run_chart_path))
            plt.title(name)
            bar_offset = bar_width*2 #/2
            for scenario in data_to_plot:
                for weight in data_to_plot[scenario]:
                    #if bottoms == 0:
                    #    bottoms = np.zeros(len(data_to_plot[scenario][weight].keys()))
                    #plt.bar([(xi + bar_offset) for xi in  list(data_to_plot[scenario][weight].keys())],
                    #        list(data_to_plot[scenario][weight].values()),
                    #        width = bar_width,
                    #        color=color_code[scenario][weight],
                    #        label="{0} - {1}".format(scenario,weight),
                    #        bottom=bottoms
                    #        )
                    plt.plot(list(data_to_plot[scenario][weight].keys()),
                            list(data_to_plot[scenario][weight].values()),
                            color=color_code[scenario][weight],
                            label="{0} - {1}".format(scenario,weight)
                            )

                bar_offset += bar_width*2
                    #bottoms += np.any(list(data_to_plot[scenario][weight].values()))
            plt.legend()
            self.add_timestamp(plt)
            plt.savefig(tp_run_chart_path)
        return

    def plot_them_all(self, mc_result):

        ##### to plot (from file and simulation)
        atmosphere_to_plot = {}
        atmosphere_to_plot['data'] = mc_result['data']['state_of_atmosphere']
        atmosphere_to_plot['sc1'] = mc_result['sc1']['atmosphere_to_plot']
        atmosphere_to_plot['sc2'] = mc_result['sc2']['atmosphere_to_plot']
        atmosphere_to_plot['sc3'] = mc_result['sc3']['atmosphere_to_plot']
        self.plot_mc_results(atmosphere_to_plot,"state_of_atmosphere")

        capital_nature_to_plot = {}
        capital_nature_to_plot['data'] = mc_result['data']['capital_nature']
        capital_nature_to_plot['sc1'] = mc_result['sc1']['capital_nature_to_plot']
        capital_nature_to_plot['sc2'] = mc_result['sc2']['capital_nature_to_plot']
        capital_nature_to_plot['sc3'] = mc_result['sc3']['capital_nature_to_plot']
        self.plot_mc_results(capital_nature_to_plot,"capital_nature", type="bar")

        capital_nature_sc3 = {}
        capital_nature_sc3['sc3'] = mc_result['sc3']['capital_nature_to_plot']
        self.plot_mc_results(capital_nature_sc3,"capital_nature_sc3")


        eco_performance_to_plot = {}
        eco_performance_to_plot['data'] = mc_result['data']['eco_performance']
        eco_performance_to_plot['sc1'] = mc_result['sc1']['eco_performance_to_plot']
        eco_performance_to_plot['sc2'] = mc_result['sc2']['eco_performance_to_plot']
        eco_performance_to_plot['sc3'] = mc_result['sc3']['eco_performance_to_plot']

        self.plot_mc_results(eco_performance_to_plot,"eco_performance")

        gdp_to_plot = {}
        gdp_to_plot['data'] = mc_result['data']['gdp']
        gdp_to_plot['sc1'] = mc_result['sc1']['gdp_to_plot']
        gdp_to_plot['sc2'] = mc_result['sc2']['gdp_to_plot']
        gdp_to_plot['sc3'] = mc_result['sc3']['gdp_to_plot']
        self.plot_mc_results(gdp_to_plot,"gdp")

        success_to_plot = {}
        success_to_plot['data'] = mc_result['data']['success']
        success_to_plot['sc1'] = mc_result['sc1']['success_to_plot']
        success_to_plot['sc2'] = mc_result['sc2']['success_to_plot']
        success_to_plot['sc3'] = mc_result['sc3']['success_to_plot']
        self.plot_mc_results(success_to_plot,"success")

        capital_total_to_plot = {}
        capital_total_to_plot['data'] = {}
        capital_total_to_plot['data']['business'] = mc_result['data']['capital_business']
        capital_total_to_plot['data']['nature'] = mc_result['data']['capital_nature']
        capital_total_to_plot['sc1'] = {}
        capital_total_to_plot['sc1']['business'] = mc_result['sc1']['capital_business_to_plot']
        capital_total_to_plot['sc1']['nature'] = mc_result['sc1']['capital_nature_to_plot']


        capital_total_to_plot['sc2'] = {}
        capital_total_to_plot['sc2']['business'] = mc_result['sc2']['capital_business_to_plot']
        capital_total_to_plot['sc2']['nature'] = mc_result['sc2']['capital_nature_to_plot']
        capital_total_to_plot['sc3'] = {}
        capital_total_to_plot['sc3']['business'] = mc_result['sc3']['capital_business_to_plot']
        capital_total_to_plot['sc3']['nature'] = mc_result['sc3']['capital_nature_to_plot']
        self.plot_capital_weight(capital_total_to_plot, "capital_weights")

        return

    def plot_planetary_boundary_forecast(self, regression_line, pb_forecast_sc1, pb_forecast_sc2):

        if self.save_charts:
            tp_run_chart_path = os.path.join(self.charts_folder, 'Forecast_Chart_{0}.png'.format(self.current_date))
            plt.figure(figsize=(15, 9))

            print("Storing Chart at {0}".format(tp_run_chart_path))

            plt.plot(list(regression_line.keys()), list(regression_line.values()), color='red', linestyle='-',label='Regression line')

            ### Plot Scenario 1
            plt.scatter(pb_forecast_sc1.keys(), pb_forecast_sc1.values(), color='blue',label='Scenario Business as usual')  # Punkte plotten
            plt.plot(pb_forecast_sc1.keys(), pb_forecast_sc1.values(), color='lightblue', linestyle='--')  # Verbindungslinie (optional)

            ### Plot Scenario 1
            plt.scatter(pb_forecast_sc2.keys(), pb_forecast_sc2.values(), color='green',label='Scenario Feedbackloop Planetary Boundary')  # Punkte plotten
            plt.plot(pb_forecast_sc2.keys(), pb_forecast_sc2.values(), color='lightgreen', linestyle='--')  # Verbindungslinie (optional)

            # Achsenbeschriftungen
            plt.xlabel('Jahre', fontsize=12)
            plt.ylabel('Co2 Anteil in der Atmosphäre in ppm', fontsize=12)
            plt.title('Vorhersage Planetare Grenzen', fontsize=14)

            # Gitternetz und Legende
            plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
            plt.legend()
            plt.ylim(0, 1000)#max(list(pb_forecast_sc1.values()), pb_forecast_sc2.values(), list(regression_line.values()))+10)

            self.add_timestamp(plt)
            plt.savefig(tp_run_chart_path)

        print("Found {0} prediction items to plot for scenario 1".format(len(pb_forecast_sc1)))
        print("Found {0} prediction items to plot for scenario 2".format(len(pb_forecast_sc2)))

        return

    def add_timestamp(self, plt):
        plt.text(1, 1.02, f"Generated on {self.current_date}", transform=plt.gca().transAxes, fontsize=10, ha='right', va='top')

    def z_test(self):
        sample =[419,420,420,425]
        # Gegebene Werte
        mu0 = 420                       # Nullhypothese (populationsmittelwert)
        x_bar = mean(sample)            # Stichprobenmittelwert
        sigma = 1                       # Populationsstandardabweichung
        n = len(sample)                 # Stichprobengröße
        alpha = 0.05                    # Signifikanzniveau

        # Berechnung des z-Werts
        z = (x_bar - mu0) / (sigma / (n ** 0.5))

        # Kritischen z-Wert für einseitigen Test berechnen
        z_critical = norm.ppf(1 - alpha)  # 1-alpha für oberen Bereich

        # Ergebnis des Tests
        print(f"Z-Wert der Stichprobe: {z:.2f}")
        print(f"Kritischer Z-Wert: {z_critical:.2f}")

        if z > z_critical:
            print("Ergebnis: Die Nullhypothese wird abgelehnt. Die Maschine stellt signifikant zu schwere Produkte her.")
        else:
            print("Ergebnis: Die Nullhypothese kann nicht abgelehnt werden. Es gibt keine signifikanten Hinweise darauf, dass die Produkte zu schwer sind.")

    def __format_validation(self, mc_result, name="default"):
        print("==============================")
        print("=== FORMAT validation: {0} ===".format(name))
        list_keys = sorted(mc_result.keys())
        for key in list_keys:
            print ("{0}: {1}".format(key,mc_result[key]))
        print("=== end of FORMAT validation: {0} ===".format(name))
        print("==============================")
        return
