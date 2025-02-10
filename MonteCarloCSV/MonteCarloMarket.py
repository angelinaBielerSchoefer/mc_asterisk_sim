import math
import sys

import numpy as np
import os
import random

from collections import Counter
from Company import Company
from concurrent.futures import ProcessPoolExecutor
from datetime import  datetime
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
                 assume,
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

        #script_dir = os.path.dirname(os.path.abspath(__file__))

    def start_simulation(self,
                         data_atmosphere_year_value,
                         data_bvbig_year_value,
                         data_capbig_year_value,
                         data_co2_free_allowances_value,
                         data_co2_price_year_value,
                         data_co2_sold_allowances_value,
                         data_co2_subvention_value,
                         data_emissions_year_value,
                         data_gdp_year_value,
                         data_investment_by_category_year_value,
                         data_total_assets_year_value,
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
        mc_result['data']['investment_by_company_category'] = data_investment_by_category_year_value# million eur per staff-size???
        mc_result['data']['gdp'] = data_gdp_year_value # in million euro
        mc_result['data']['free_allowances'] = data_co2_free_allowances_value #metric tone
        mc_result['data']['sold_allowances'] = data_co2_sold_allowances_value #metric tone
        mc_result['data']['co2_subvention'] = data_co2_subvention_value #metric tone
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

        #for year, entry in mc_result['sc1'][0]['co2_market'].journal.items():
        #    print("year {0}:co2_intensity {1}".format(year,entry['co2_intensity']))

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

        #test value taken from sampel
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
    def __run_simulation_competitive_pricing_parallel(self):
        mc_result = {}
        with ProcessPoolExecutor() as executor:
            keys = list(range(self.trials_market))
            result = executor.map(self.simulate_one_trial_of_market_competitive, keys)
            mc_result=dict(zip(keys, result))

        return mc_result

    def __prerun_data_input(self, data_collection):

        data_collection['business_power']       = {}
        data_collection['capital_business']     = {}
        data_collection['capital_nature']       = {}
        data_collection['co2_consumption']      = {}
        data_collection['co2_emission']         = {}
        data_collection['co2_intensity']        = {}
        data_collection['co2_investment']       = {}
        data_collection['delta_capital']        = {}
        data_collection['delta_capital_nature'] = {}
        data_collection['delta_co2_emission']   = {}
        data_collection['delta_co2_intensity']  = {}
        data_collection['delta_co2_price']      = {}
        data_collection['delta_co2_subvention'] = {}
        data_collection['delta_free_allowances'] = {}
        data_collection['delta_sale_allowances'] = {}
        data_collection['delta_gdp']            = {}
        data_collection['eco_performance']      = {}
        data_collection['market_conditions']    = {}
        data_collection['sales_volume_category']= {}
        data_collection['share_of_co2_investment'] = {}
        data_collection['share_of_co2_idle']    = {}
        data_collection['share_of_gdp']         = {}
        data_collection['share_of_total_assets']= {}

        cnt_y = 1980
        while cnt_y < 2024:
            if cnt_y in data_collection['verified_co2_emission'] and cnt_y in data_collection['free_allowances'] and cnt_y in data_collection['sold_allowances']:
                data_collection['co2_emission'][cnt_y] = data_collection['verified_co2_emission'][cnt_y] +data_collection['free_allowances'][cnt_y] + data_collection['sold_allowances'][cnt_y]

            if cnt_y in data_collection['co2_emission'] and cnt_y in data_collection['business_values']:
                data_collection['co2_intensity'][cnt_y] = data_collection['co2_emission'][cnt_y] /  data_collection['business_values'][cnt_y]
            if cnt_y in data_collection['co2_emission'] and cnt_y-1 in data_collection['co2_emission']:
                data_collection['delta_co2_emission'][cnt_y] = [data_collection['co2_emission'][cnt_y] - data_collection['co2_emission'][cnt_y-1]]
            if cnt_y in data_collection['gdp'] and (cnt_y-1) in data_collection['gdp']:
                data_collection['delta_gdp'][cnt_y] = data_collection['gdp'][cnt_y] - data_collection['gdp'][cnt_y-1]
            if cnt_y in data_collection['co2_intensity'] and (cnt_y-1) in data_collection['co2_intensity']:
                data_collection['delta_co2_intensity'][cnt_y] = [data_collection['co2_intensity'][cnt_y] - data_collection['co2_intensity'][cnt_y-1]]
            if cnt_y in data_collection['co2_price']:
                data_collection['co2_price'][cnt_y] =[data_collection['co2_price'][cnt_y]]
            if cnt_y in data_collection['co2_price'] and (cnt_y-1) in data_collection['co2_price']:
                data_collection['delta_co2_price'][cnt_y] = [data_collection['co2_price'][cnt_y][-1] - data_collection['co2_price'][cnt_y-1][-1]]
            if cnt_y in data_collection['co2_subvention'] and (cnt_y-1) in data_collection['co2_subvention']:
                data_collection['delta_co2_subvention'][cnt_y] = [data_collection['co2_subvention'][cnt_y] - data_collection['co2_subvention'][cnt_y-1]]
            if cnt_y in data_collection['free_allowances'] and (cnt_y-1) in data_collection['free_allowances']:
                data_collection['delta_free_allowances'][cnt_y] = [data_collection['free_allowances'][cnt_y] - data_collection['free_allowances'][cnt_y-1]]
            if cnt_y in data_collection['sold_allowances'] and (cnt_y-1) in data_collection['sold_allowances']:
                data_collection['delta_sale_allowances'][cnt_y] = [data_collection['sold_allowances'][cnt_y] - data_collection['sold_allowances'][cnt_y-1]]
            if cnt_y in data_collection['verified_co2_emission'] and cnt_y in data_collection['co2_emission']:
                data_collection['share_of_co2_idle'][cnt_y] = data_collection['verified_co2_emission'][cnt_y] / data_collection['co2_emission'][cnt_y]
            if cnt_y in data_collection['business_values'] and cnt_y in data_collection['gdp']:
                data_collection['share_of_gdp'][cnt_y] = [data_collection['business_values'][cnt_y] / data_collection['gdp'][cnt_y]]
            if cnt_y in data_collection['capitals'] and cnt_y in data_collection['total_assets']:
                data_collection['share_of_total_assets'][cnt_y] = [data_collection['capitals'][cnt_y] / data_collection['total_assets'][cnt_y]]
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



            if cnt_y in data_collection['investment_by_company_category']['unter 2 Mill EUR']:
                for category in data_collection['assume']['prop_sales_volume']:
                    if not category in data_collection['sales_volume_category']:
                        data_collection['sales_volume_category'][category] = {}
                    if not cnt_y in data_collection['sales_volume_category'][category]:
                        data_collection['sales_volume_category'][category][cnt_y] = []
                    match category:
                        case 'u2':
                            value = data_collection['investment_by_company_category']['unter 2 Mill EUR'][cnt_y]
                            data_collection['sales_volume_category'][category][cnt_y] = value
                        case '2-10':
                            value = data_collection['investment_by_company_category']['2 bis unter 5 Mill EUR'][cnt_y]
                            value += data_collection['investment_by_company_category']['5 bis unter 10 Mill EUR'][cnt_y]
                            data_collection['sales_volume_category'][category][cnt_y] = value
                        case '10-50':
                            value = data_collection['investment_by_company_category']['10 bis unter 20 Mill EUR'][cnt_y]
                            value += data_collection['investment_by_company_category']['20 bis unter 50 Mill EUR'][cnt_y]
                            data_collection['sales_volume_category'][category][cnt_y] = value
                        case 'o50':
                            value = data_collection['investment_by_company_category']['50 Mill EUR und mehr'][cnt_y]
                            data_collection['sales_volume_category'][category][cnt_y] = value

            investment = 0
            for category,entry in data_collection['investment_by_company_category'].items():
                if cnt_y in entry:
                    investment+= entry[cnt_y]

            if not investment == 0 and cnt_y in data_collection['total_assets']:
                data_collection['co2_investment'][cnt_y] = [investment]
                data_collection['share_of_co2_investment'][cnt_y] = [investment/data_collection['total_assets'][cnt_y]]

            ### calc delta capital
            if cnt_y in data_collection['total_assets'] and cnt_y-1 in data_collection['total_assets']:
                data_collection['delta_capital'][cnt_y] = data_collection['total_assets'][cnt_y] - data_collection['total_assets'][cnt_y-1]
                data_collection['capital_business'][cnt_y] = data_collection['total_assets'][cnt_y]
                data_collection['capital_nature'][cnt_y] = 0.0
            if cnt_y in data_collection['co2_investment'] and (cnt_y-1) in data_collection['co2_investment']:
                data_collection['delta_capital_nature'][cnt_y] = [data_collection['co2_investment'][cnt_y][-1] - data_collection['co2_investment'][cnt_y-1][-1]]
            cnt_y+=1

        data_collection['business_power']       = self.__calc_business_power(data_collection['gdp'], data_collection['delta_capital'])
        data_collection['market_conditions']    = self.__calc_market_conditions(data_collection['delta_gdp'], data_collection['total_assets'])
        #Create simulation base
        data_collection['business_power_pi']            = self.create_sim_base(data_collection['business_power'])
        data_collection['business_value_share_pi']      = self.create_sim_base(data_collection['share_of_gdp'])
        data_collection['capital_share_pi']             = self.create_sim_base(data_collection['share_of_total_assets'])
        data_collection['co2_consumption_pi']           = self.create_sim_base(data_collection['co2_consumption'])

        data_collection['co2_investment_share_pi']      = self.create_sim_base(data_collection['share_of_co2_investment'])
        data_collection['co2_price_pi']                 = self.create_sim_base(data_collection['co2_price'])
        data_collection['delta_capital_nature_pi']      = self.create_sim_base(data_collection['delta_capital_nature'])
        data_collection['delta_co2_emission_pi']        = self.create_sim_base(data_collection['delta_co2_emission'])
        data_collection['delta_co2_intensity_pi']       = self.create_sim_base(data_collection['delta_co2_intensity'])
        data_collection['delta_co2_price_pi']           = self.create_sim_base(data_collection['delta_co2_price'])
        data_collection['delta_co2_subvention_pi']      = self.create_sim_base(data_collection['delta_co2_subvention'])
        data_collection['delta_free_allowances_pi']      = self.create_sim_base(data_collection['delta_free_allowances'])
        data_collection['delta_sale_allowances_pi']      = self.create_sim_base(data_collection['delta_sale_allowances'])
        #
        #




        # parallel loop
        categories = list(data_collection['sales_volume_category'].keys())
        investments = list(data_collection['sales_volume_category'].values())

        with ProcessPoolExecutor() as executor:
            invest_delta = executor.map(self.calc_delta_investment_for_one_cat,investments)
            results = executor.map(self.create_sim_base, invest_delta)
            data_collection['investment_by_category_pi'] = dict(zip(categories, results))
        data_collection['market_conditions_pi']         = self.create_sim_base(data_collection['market_conditions'])


        return data_collection
    def __create_general_market(self,
                                business_power_pi,
                                business_value_share_start,
                                capital_share_start,
                                co2_emission_total_start,
                                co2_investment_share_pi,
                                gdp_start,
                                investment_by_category,
                                market_condition_pi,
                                total_assets_start
                                ):
        general_market = MarketGeneral(self.assume,
                                       business_power_pi,
                                       business_value_share_start,
                                       capital_share_start,
                                       co2_emission_total_start,
                                       co2_investment_share_pi,
                                       gdp_start,
                                       investment_by_category,
                                       market_condition_pi,
                                       self.start_year,
                                       total_assets_start
                                       )

        company_list = self.__create_company_list(general_market)

        return company_list, general_market

    def __create_company_list(self, general_market):
        cnt_com=0
        com_list = {}
        while cnt_com<self.number_companies:
            business_value_start, capital_start, weight_nature_start = general_market.sim_start_of_company(self.number_companies)
            company = Company(business_value_start, capital_start, weight_nature_start)
            company.business_power, company.is_alive, company.market_influence = general_market.sim_general_market_situation_company(company)
            com_list[cnt_com] = company
            cnt_com+= 1
        general_market.sim_start_rest_of_the_world(com_list)
        return com_list

    def __create_co2_market(self,
                            co2_emission_big_share_start,
                            co2_emission_total_start,
                            co2_intensity_start,
                            co2_price_start,
                            co2_subvention_start,
                            co2_supply_start,
                            company_list,
                            delta_capital_nature_pi,
                            delta_co2_emission_pi,
                            delta_co2_intensity_pi,
                            delta_co2_price_pi,
                            delta_co2_subvention_pi,
                            delta_free_allowances_pi,
                            delta_sale_allowances_pi,
                            free_allowances_start,
                            sale_allowances_start,
                            rest_of_the_world,
                            share_of_idle
                            ):
        co2_emission_big_start = co2_emission_total_start * co2_emission_big_share_start

        co2_market = MarketCo2(self.assume,
                               co2_emission_big_start,
                               co2_intensity_start,
                               co2_price_start,
                               co2_subvention_start,
                               co2_supply_start,
                               delta_capital_nature_pi,
                               delta_co2_emission_pi,
                               delta_co2_intensity_pi,
                               delta_co2_price_pi,
                               delta_co2_subvention_pi,
                               delta_free_allowances_pi,
                               delta_sale_allowances_pi,
                               free_allowances_start,
                               sale_allowances_start,)

        rest_of_the_world.co2_emission = co2_emission_total_start - co2_emission_big_start
        rest_of_the_world.co2_intensity = co2_market.co2_intensity

        for index in company_list:
            company = company_list[index]
            ## calc start value for intensity and co2_emissions
            company.co2_emission, company.co2_intensity, company.co2_emission_idle, company.co2_subvention = co2_market.calc_company_start_situation(company.business_value,
                                                                                                                             share_of_idle)
        return co2_market

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


    def simulate_one_trial_of_market_competitive(self, trials_id):
        progress_counter = 0
        target_year = 2030
        dead_list = {}
        company_list, general_market = self.__create_general_market(
            self.mc_data['business_power_pi'],
            self.mc_data['share_of_gdp'][self.start_year][-1],
            self.mc_data['share_of_total_assets'][self.start_year][-1],
            self.mc_data['co2_emission'][self.start_year],
            self.mc_data['co2_investment_share_pi'],
            self.mc_data['gdp'][self.start_year],
            self.mc_data['sales_volume_category'],
            self.mc_data['market_conditions_pi'],
            self.mc_data['total_assets'][self.start_year])

        co2_market = self.__create_co2_market(  self.assume['share_of_co2'],
                                                self.mc_data['co2_emission'][self.start_year],
                                                self.mc_data['co2_intensity'][self.start_year],
                                                self.mc_data['co2_price'][self.start_year][-1],
                                                self.mc_data['co2_subvention'][self.start_year],
                                                30000,
                                                company_list,
                                                self.mc_data['delta_capital_nature_pi'],
                                                self.mc_data['delta_co2_emission_pi'],
                                                self.mc_data['delta_co2_intensity_pi'],
                                                self.mc_data['delta_co2_price_pi'],
                                                self.mc_data['delta_co2_subvention_pi'],
                                                self.mc_data['delta_free_allowances_pi'],
                                                self.mc_data['delta_sale_allowances_pi'],
                                                self.mc_data['free_allowances'][self.start_year],
                                                self.mc_data['sold_allowances'][self.start_year],
                                                general_market.rest_of_the_world,
                                                self.assume['share_of_idle']
                                                )

        year = self.start_year

        while year < target_year:
            ### simulate
            progress_counter +=1
            self.__simulate_one_year_of_market_competitive(company_list, co2_market, general_market, year)

            #############################grant free allowances##############################################
            self.__authorize_free_allowances(co2_market,company_list)

            #############################Sale Allowances##############################################
            self.__trade_allowances(co2_market, company_list)
            #############################Voluntary Carbon Market##############################################
            demander = []
            supplier = []
            self.__trade_carbon_voluntarily(demander, supplier)
            #############################taxes##############################################
            self.__collect_taxes()
            company_list = {index:company_list[index] for index in company_list if company_list[index].is_alive}
            dead_list = {index:company_list[index] for index in company_list if not company_list[index].is_alive}
            ### for progress check on long runs
            if progress_counter % 10 == 0:
                total = (target_year-self.start_year)
                print("Trial: {0} Progress: {1} %".format(trials_id, round(100*progress_counter/total,2)))

            year += 1
        mc_result={

            'company_list'  : company_list,
            'co2_market'    : co2_market,
            'dead_list'     : dead_list,
            'general_market': general_market
        }
        return mc_result

    def __simulate_one_year_of_market_competitive(self, company_list, co2_market, general_market, year):

        ###1. Sim general market
        general_market.count_company = len(company_list)
        general_market.sim_new_year()

        total_capital_nature = co2_market.sim_new_year_co2()
        sum_cap_n = sum([company_list[index].capital_nature for index in company_list])
        general_market.rest_of_the_world.capital_nature = total_capital_nature - sum_cap_n

        self.__run_company_market(general_market.rest_of_the_world,general_market)
        gdp = general_market.rest_of_the_world.business_value
        cnt_total_capital = general_market.rest_of_the_world.capital
        cnt_big_co2 = 0
        cnt_capital_nature = general_market.rest_of_the_world.capital_nature
        for index in company_list:
            company=company_list[index]
            self.__run_company_market(company,general_market)
            self.__run_company_co2(company, co2_market)
            company.log_to_journal(year)

            gdp += company.business_value
            cnt_total_capital += company.capital
            cnt_big_co2 += company.co2_emission #in  mio metric tons
            cnt_capital_nature+=company.weight_nature


        total_co2 = general_market.rest_of_the_world.co2_emission + cnt_big_co2

        ###4. calc general market
        general_market.total_assets = cnt_total_capital
        general_market.gdp = gdp


        general_market.co2_emission_total = total_co2
        ###5. calc co2 market
        co2_market.co2_emission_big = cnt_big_co2
        co2_market.total_capital_nature = cnt_capital_nature

        ## log all infos
        co2_market.log_to_journal(year)
        general_market.log_to_journal(year)
        return
    def __compensate_co2_sc1(self, company_list):
        return
    def __authorize_free_allowances(self, co2_market, company_list):
        total_co2_free_apply = sum([company_list[index].co2_apply_free for index in company_list])
        cscf = co2_market.calc_cross_sectoral_correction_factor(total_co2_free_apply)
        for index in company_list:
            company = company_list[index]
            freeCo2 = company.co2_emission * cscf
            co2_market.invoice['free'].append((company, co2_market, 0.0, freeCo2))
            company.co2_demand = company.co2_emission - freeCo2

        return cscf

    def __trade_allowances(self, co2_market, company_list):
        demander_list = co2_market.price_finding_to_sale_allowances(company_list)
        sold_allowances = 0
        demander_with_remaining_stock = []
        while co2_market.sale_allowances > sold_allowances and len(demander_list) > 0:

            id = random.randint(-1 , len(demander_list)-1)
            demander = demander_list[id]
            decrease = 0
            if (demander.co2_demand + sold_allowances) <= co2_market.sale_allowances:
                sold_allowances += demander.co2_demand
                decrease = demander.co2_demand
            else:
                decrease = co2_market.sale_allowances - sold_allowances

            price = decrease * co2_market.co2_price

            if price < demander.capital_nature:
                demander.co2_demand -= decrease
                demander.capital_nature -= price
                sold_allowances += decrease
                co2_market.invoice['sale'].append((demander, co2_market, decrease, price))
            else:
                demander_with_remaining_stock.append(demander)

            demander_list.remove(demander)


        print("new price for {0} demander".format(len(demander_with_remaining_stock)))
        print("{0} allowances of {1} sold:".format(sold_allowances,co2_market.sale_allowances))

        return demander_list

    def __trade_carbon_voluntarily(self, demander, supplier):


        return 0
    def __collect_taxes(self):
        total_taxes = 0
        return total_taxes

    def __run_company_co2(self, company, co2_market):
        business_value = company.business_value
        capital = company.capital
        co2_intensity_last_year = company.co2_intensity
        co2_subvention_last_year = company.co2_subvention
        company.co2_intensity,company.capital_nature, company.co2_apply_free, company.co2_emission= co2_market.calc_co2_market_situation_company(
            business_value,
            capital,
            company.co2_emission_idle,
            co2_intensity_last_year,
            co2_subvention_last_year,
            company.weight_nature)

    def __run_company_market(self, company, general_market):

        business_value_last_year = company.business_value
        capital_last_year = company.capital_business
        ###2. sim general_market conditions for this single company
        company.business_power, company.is_alive, company.market_influence = general_market.sim_general_market_situation_company(company)
        ###3. calc company status related to general market conditions
        company.business_value, company.capital, company.capital_business, company.capital_nature, company.delta_capital, company.delta_business_value = general_market.calc_general_situation_company(
            company.business_power,
            business_value_last_year,
            capital_last_year,
            company.market_influence,
            company.weight_nature
        )


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

    def create_sim_base(self, data_to_sim):
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
    def calc_delta_investment_for_one_cat(self,data_investment_year_value):
        investments = {}

        value_last_year = 0.0
        start_year = min(data_investment_year_value.keys())
        for year,value in data_investment_year_value.items():
            if not year in investments:
                investments[year] = []
            if not year == start_year:
                investments[year].append(value - value_last_year)
            value_last_year = value
        return investments

    def plot_mc_results(self, data_to_plot, name,unit ):
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



            min_2020 = 0
            max_2020 = 0

            for scenario in data_to_plot:
                x = list(data_to_plot[scenario].keys())
                if scenario =="data":
                    y = [entry['mean'] for key, entry in sorted(data_to_plot[scenario].items())]

                    plt.plot(x, y, color=color_code[scenario], linestyle='-',label=scenario)

                if not scenario =="data":
                    min_2020 = float(round(data_to_plot[scenario][2020]['min'],0))
                    max_2020 = float(round(data_to_plot[scenario][2020]['max'],0))
                    lower_bound = [entry['min'] for key, entry in sorted(data_to_plot[scenario].items())]
                    upper_bound = [entry['max'] for key, entry in sorted(data_to_plot[scenario].items())]
                    plt.fill_between(x, lower_bound, upper_bound, color=color_code[scenario], alpha=0.2, label='95% confidence interval {0}'.format(scenario))

            plt.legend()


            confi_interval = (min_2020, max_2020)
            self.add_timestamp(plt,confi_interval)
            plt.savefig(tp_run_chart_path)
        return

    def plot_mc_results_bar(self, data_to_plot, target_value, name="default", type="bar"):
        if self.save_charts:
            tp_run_chart_path = os.path.join(self.charts_folder, '{0}_{1}_mc_bars.png'.format(self.current_date,name))
            plt.figure(figsize=(15, 9))

            color_code = {}
            color_code['data'] = 'red'
            color_code['sc1'] = 'black'
            color_code['sc2'] = 'blue'
            color_code['sc3'] = 'green'



            print("Storing Chart at {0}".format(tp_run_chart_path))
            plt.title("{0} ".format(name))

            offset = -0.04
            for scenario in data_to_plot:
                sorted_data = sorted(data_to_plot[scenario],reverse=True)
                print("given format:{0}".format(sorted_data))
                sorted_data = [12.45,12.45,12.46,12.46,12.47,12.47,12.47,12.47,12.47,12.48,12.48,12.48,12.48,12.48,12.48,12.48,12.49,12.49,12.49,12.49,12.49,12.49,12.49,12.49]
                print("target format:{0}".format(sorted_data))
                data = Counter(sorted_data)

                plt.bar([x + offset for x in data],
                        list(data.values()),
                        width=0.02,
                        color=color_code[scenario],
                        linestyle='-',
                        label=scenario)
                offset+= 0.02
            plt.legend()
            self.add_timestamp(plt)
            plt.savefig(tp_run_chart_path)
        return
    def plot_results(self, mc_result):


        self.plot_data = mc_result

        # plot_labels legend
        # [0] = market
        # [1] = name of plot file and title
        # [2] = label in data
        # [3] = label in scenarios
        # [4] = unit

        plot_labels = [
            ('co2_market', 'capital_nature', 'co2_investment', 'total_capital_nature','mrd Euro'),
            ('co2_market', 'Co2_Price', 'co2_price', 'co2_price','US $ / mio metric tons Co2 equivalence'),
            ('general_market', 'Count_company', '', 'count_company','number of surviving companies'),
            ('general_market', 'Co2_Emission_total', 'co2_emission', 'co2_emission_total','mio metric tones Co2 Emission'),
            ('co2_market', 'Co2_Intensity', 'co2_intensity', 'co2_intensity','mio metric tones Co2 Emission per mrd Euro'),
            ('co2_market', 'Co2_Subvention', 'co2_subvention', 'co2_subvention','in mrd Euro'),
            ('co2_market', 'Free_allowances', 'free_allowances', 'free_allowances','in ??? Co2'),

            ('co2_market', 'Sold_Allowances', 'sold_allowances', 'sale_allowances','in ??? Co2'),
            ('general_market', 'gdp', 'gdp', 'gdp', 'in Mrd Euro'),
            ('general_market', 'capital', 'capital_business', 'total_assets', 'in Mrd Euro')
        ]
        #self.transform_data_and_plot(('general_market', 'Count_company', '', 'count_company','number of surviving companies'),)
        with ProcessPoolExecutor() as executor:
            keys = plot_labels
            executor.map(self.transform_data_and_plot, keys)
        return

    def transform_data_and_plot(self, tuple):
        mc_result = self.plot_data
        # tuple
        # [0] = market
        # [1] = name of plot file and title
        # [2] = label in data
        # [3] = label in scenarios
        # [4] = unit
        market = tuple[0]
        data = {}
        plot_name = tuple[1]
        data_label = tuple[2] #plot_label[0]
        sce_label = tuple[3] #plot_label[1]
        unit = tuple[4]

        data['data'] = {}
        if not data_label == '':
            for year,value in mc_result['data'][data_label].items():
                data['data'][year] = {'mean': value}

        for scenario in mc_result:
            if not scenario in data:
                data[scenario] = {}
            if not scenario == 'data':
                trial_list = {}

                for cnt in mc_result[scenario]:
                    year = self.start_year
                    while year in mc_result[scenario][cnt][market].journal:
                        if not year in data[scenario]:
                            data[scenario][year] = {}
                        if not year in trial_list:
                            trial_list[year] = []
                        trial_list[year].append(mc_result[scenario][cnt][market].journal[year][sce_label])
                        mean_v = mean(trial_list[year])
                        min_v = np.percentile(trial_list[year], 2.5, axis=0)  # lower 2.5%
                        max_v = np.percentile(trial_list[year], 97.5, axis=0)  # upper 97.5%
                        data[scenario][year]['min'] = min_v
                        data[scenario][year]['mean'] = mean_v
                        data[scenario][year]['max'] = max_v
                        year+= 1

        self.plot_mc_results(data, plot_name, unit)
        return



    def add_timestamp(self, plt, confidence_interval = (0.0, 0.0)):
        plt.text(1, 1.02, f"Generated on {self.current_date}", transform=plt.gca().transAxes, fontsize=10, ha='right', va='top')


        note_text = ("Number of companies: {0}\n"
                     "Market trials:{1}\n"
                     "stdev business power: {2}\n"
                     "stdev market_influence: {3}\n"
                     "stdev start value gdp: {4}\n"
                     "stdev start value Total Assets: {5}\n"
        .format(
            self.number_companies,
            self.trials_market,
            self.assume['stdev_business_power'],
            self.assume['stdev_market_influence'],
            (self.assume['stdev_start_value']/self.number_companies),
            (self.assume['stdev_start_assets']/self.number_companies),
        ))

        if not (confidence_interval[0] == 0.0 and confidence_interval[1] == 0.0):
            note_text = ("{0}"
                         "sc1: confidence interval (2020): {1}\n").format(note_text, confidence_interval)

        plt.text(0.1, 0.9, note_text, transform=plt.gca().transAxes,fontsize=10, va='top', ha='left', color='blue')


    def __format_validation(self, mc_result, name="default"):
        print("==============================")
        print("=== FORMAT validation: {0} ===".format(name))
        list_keys = sorted(mc_result.keys())
        for key in list_keys:
            print ("{0}: {1}".format(key,mc_result[key]))
        print("=== end of FORMAT validation: {0} ===".format(name))
        print("==============================")
        return
    def __size_recalc(self):
        #self.slim_data = np.zeros((self.trials_market,target_year-self.start_year,self.number_companies,5))


        list_data = []
        dict_data = {}
        array_data = np.zeros((5,2))
        tuple_data = ()

        t_trials = 10000
        t_com = 500000
        t_years = 22
        t_variables = 10
        for var in range(t_variables):
            list_data.append([])
            tuple_data.__add__(())
            for year in range(t_years):
                tuple_data[var].__add__(())
                list_data[var].append([])
                for com in range(t_com):
                    tuple_data[var][com].__add__(())
                    list_data[var][com].append([])
                    for trial in range(t_trials):
                        list_data[var][com][year].append(1.0)
                        tuple_data[var][com][year].__add__(1.0)

        print ("sizeof list data: {0}".format(sys.getsizeof(list_data)))
        print ("sizeof dict data: {0}".format(sys.getsizeof(dict_data)))
        print ("sizeof array data: {0}".format(sys.getsizeof(array_data)))
        print ("sizeof tuple data: {0}".format(sys.getsizeof(tuple_data)))