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
                 start_year = 2008,
                 target_year = 2050,
                 ):
        self.assume = assume
        self.number_companies = number_companies
        self.parallel = parallel
        self.save_charts = save_charts
        self.start_year = start_year
        self.target_year = target_year
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
                         data_carbon_credits_year_value,
                         data_co2_emission_global_year_value,
                         data_co2_free_allowances_value,
                         data_co2_price_year_value,
                         data_co2_sold_allowances_value,
                         data_co2_subvention_value,
                         data_company_grow_rate_year_value,
                         data_verified_emissions_year_value,
                         data_gdp_year_value,
                         data_investment_by_category_year_value,
                         data_price_allowances_year_value,
                         data_price_credit_year_value,
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
        mc_result['data']['carbon_credits'] = data_carbon_credits_year_value# mio metric tone
        mc_result['data']['co2_emission_global'] = data_co2_emission_global_year_value
        mc_result['data']['co2_subvention'] = data_co2_subvention_value #metric tone
        mc_result['data']['grow_rate'] = data_company_grow_rate_year_value # no unit
        mc_result['data']['free_allowances'] = data_co2_free_allowances_value #metric tone
        mc_result['data']['gdp'] = data_gdp_year_value # in million euro
        mc_result['data']['investment_by_company_category'] = data_investment_by_category_year_value# million eur per staff-size???
        mc_result['data']['co2_price'] = data_co2_price_year_value# mrd Euro per mio metric ton
        mc_result['data']['price_allowances'] = data_price_allowances_year_value# mrd Euro per mio metric ton
        mc_result['data']['price_credit'] = data_price_credit_year_value# mrd Euro per mio metric ton
        mc_result['data']['sold_allowances'] = data_co2_sold_allowances_value #metric tone
        mc_result['data']['state_of_atmosphere'] = data_atmosphere_year_value # 420ppm in 2022
        mc_result['data']['total_assets'] = data_total_assets_year_value #unit??
        mc_result['data']['verified_co2_emission'] = data_verified_emissions_year_value # metric tone


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

        #print("----- Execution of Scenario 2 -----")
        #print("not yet Implemented")
        #mc_result['sc2'] = self.__run_simulation_scenario_two(sim_start, target_year+3,mc_result['sc1'])

        #print("----- Execution of Scenario 3 -----")
        #print("not yet Implemented")
        #mc_result['sc3']=self.__run_simulation_scenario_three(sim_start, target_year+3,mc_result['sc2'])


        sig_result = {}
        #print("----- Significance analysis 1: Validation of Success Model (Data to Sc1) -----")
        #print("not yet Implemented")
        #sig_result['val_suc_model'] = self.__validate_success_model(sim_start-1, mc_result['data'], mc_result['sc1'])

        #print("----- Significance analysis 2: Validation of ecoPerformance Model (Sc1 to Sc2) -----")
        #print("not yet Implemented")
        #sig_result['val_eco_model'] = self.__validate_eco_model(sim_start-1, mc_result['sc1'],mc_result['sc2'])


        #print("----- Significance analysis 3: Validate success optimization (Sc2 to Sc3) -----")
        #print("not yet Implemented")
        #sig_result['proof_impact'] = self.__evaluate_treatment_effect(target_year, mc_result['sc2'],mc_result['sc3'])

        self.end_time = datetime.now()
        time_needed_to_execute = self.end_time- self.start_time
        print("Time to execute: {0} for {1} companies over {2} trials".format(time_needed_to_execute, self.number_companies, self.trials_market))

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
        with ProcessPoolExecutor() as executor:
            keys = list(range(self.trials_market))
            result = executor.map(self.simulate_one_trial_of_market_competitive, keys)
            mc_result = dict(zip(keys, result))

        return mc_result

    def __prerun_data_input(self, data_collection):


        data_collection['business_power']           = {}
        data_collection['capital_total']            = {}
        data_collection['capital_business']         = {}
        data_collection['capital_nature']           = {}
        data_collection['co2_consumption']          = {}
        data_collection['co2_emission_sum']         = {}
        data_collection['co2_intensity']            = {}
        data_collection['co2_investment']           = {}
        data_collection['delta_capital']            = {}
        data_collection['delta_capital_pi_base']    = {}
        data_collection['delta_capital_nature']     = {}
        data_collection['delta_carbon_credits']     = {}
        data_collection['delta_co2_consumption']    = {}
        data_collection['delta_co2_emission_global']= {}
        data_collection['delta_co2_intensity']      = {}
        data_collection['delta_co2_price_pi_base']  = {}
        data_collection['delta_co2_subvention']     = {}
        data_collection['delta_free_allowances']    = {}
        data_collection['delta_sale_allowances']    = {}
        data_collection['delta_gdp']                = {}
        data_collection['delta_gdp_pi_base']        = {}
        data_collection['eco_performance']          = {}
        data_collection['market_conditions']        = {}
        data_collection['market_conditions_nature'] = {}
        data_collection['sales_volume_category']    = {}
        data_collection['share_of_co2_investment']  = {}
        data_collection['share_of_gdp']             = {}
        data_collection['share_of_total_assets']    = {}

        cnt_y = 1980
        while cnt_y < 2024:

            if cnt_y in data_collection['verified_co2_emission'] and cnt_y in data_collection['free_allowances'] and cnt_y in data_collection['sold_allowances']:
                data_collection['co2_emission_sum'][cnt_y] = data_collection['verified_co2_emission'][cnt_y] +data_collection['free_allowances'][cnt_y] + data_collection['sold_allowances'][cnt_y]
            if cnt_y in data_collection['co2_emission_sum'] and cnt_y in data_collection['business_values']:
                data_collection['co2_intensity'][cnt_y] = data_collection['co2_emission_sum'][cnt_y] /  data_collection['business_values'][cnt_y]

            if cnt_y in data_collection['co2_emission_global'] and (cnt_y-1) in data_collection['co2_emission_global']:
                data_collection['delta_co2_emission_global'][cnt_y] = [data_collection['co2_emission_global'][cnt_y] - data_collection['co2_emission_global'][cnt_y-1]]
            if cnt_y in data_collection['co2_intensity'] and (cnt_y-1) in data_collection['co2_intensity']:
                data_collection['delta_co2_intensity'][cnt_y] = [data_collection['co2_intensity'][cnt_y] - data_collection['co2_intensity'][cnt_y-1]]

            #if cnt_y in data_collection['co2_emission'] and cnt_y-1 in data_collection['co2_emission']:
            #    data_collection['delta_co2_emission'][cnt_y] = [data_collection['co2_emission'][cnt_y] - data_collection['co2_emission'][cnt_y-1]]
            if cnt_y in data_collection['gdp'] and (cnt_y-1) in data_collection['gdp']:
                data_collection['delta_gdp'][cnt_y] = data_collection['gdp'][cnt_y] - data_collection['gdp'][cnt_y-1]
                data_collection['delta_gdp_pi_base'][cnt_y] = [data_collection['delta_gdp'][cnt_y] ]
            #if cnt_y in data_collection['co2_price']:
            #     data_collection['co2_price'][cnt_y] =[data_collection['co2_price'][cnt_y]]
            if cnt_y in data_collection['co2_price'] and (cnt_y-1) in data_collection['co2_price']:
                data_collection['delta_co2_price_pi_base'][cnt_y] = [data_collection['co2_price'][cnt_y] - data_collection['co2_price'][cnt_y-1]]
            #if cnt_y in data_collection['co2_subvention'] and (cnt_y-1) in data_collection['co2_subvention']:
            #    data_collection['delta_co2_subvention'][cnt_y] = [data_collection['co2_subvention'][cnt_y] - data_collection['co2_subvention'][cnt_y-1]]
            #if cnt_y in data_collection['free_allowances'] and (cnt_y-1) in data_collection['free_allowances']:
            #    data_collection['delta_free_allowances'][cnt_y] = [data_collection['free_allowances'][cnt_y] - data_collection['free_allowances'][cnt_y-1]]
            #if cnt_y in data_collection['carbon_credits'] and (cnt_y-1) in data_collection['carbon_credits']:
            #    data_collection['delta_carbon_credits'][cnt_y] = [data_collection['carbon_credits'][cnt_y] - data_collection['carbon_credits'][cnt_y-1]]
            #if cnt_y in data_collection['sold_allowances'] and (cnt_y-1) in data_collection['sold_allowances']:
            #    data_collection['delta_sale_allowances'][cnt_y] = [data_collection['sold_allowances'][cnt_y] - data_collection['sold_allowances'][cnt_y-1]]

            if cnt_y in data_collection['business_values'] and cnt_y in data_collection['gdp']:
                data_collection['share_of_gdp'][cnt_y] = [data_collection['business_values'][cnt_y] / data_collection['gdp'][cnt_y]]
            if cnt_y in data_collection['capitals'] and cnt_y in data_collection['total_assets']:
                data_collection['share_of_total_assets'][cnt_y] = [data_collection['capitals'][cnt_y] / data_collection['total_assets'][cnt_y]]

            ### calc eco_performance
            if (cnt_y in data_collection['co2_emission_global']
                    and cnt_y+1 in data_collection['state_of_atmosphere']):
                r_convert = self.assume['r_convert']
                v_ppm = data_collection['co2_emission_global'][cnt_y] / r_convert ## change of atmospheric state by human impact in ppm
                atmosphere_last_year = data_collection['state_of_atmosphere'][cnt_y-1]

                data_collection['eco_performance'][cnt_y] =self.__calc_eco_impact_by_parabola(atmosphere_last_year,v_ppm)
                calc_new_atmosphere_value = atmosphere_last_year + v_ppm #in ppm
                data_new_atmosphere_value = data_collection['state_of_atmosphere'][cnt_y] # in ppm
                co2_consumption = calc_new_atmosphere_value - data_new_atmosphere_value  #calc diff in ppm
                if co2_consumption < 0:
                    co2_consumption = 0
                data_collection['co2_consumption'][cnt_y] = co2_consumption * r_convert # calc to mio metric tons


            if cnt_y in data_collection['co2_consumption'] and (cnt_y-1) in data_collection['co2_consumption']:
                data_collection['delta_co2_consumption'][cnt_y] = [data_collection['co2_consumption'][cnt_y] - data_collection['co2_consumption'][cnt_y-1]]


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


            ### calc delta capital
            if cnt_y in data_collection['total_assets']:
                data_collection['capital_total'][cnt_y] = data_collection['total_assets'][cnt_y] + investment
                data_collection['capital_business'][cnt_y] = data_collection['total_assets'][cnt_y]
                if investment != 0:
                    data_collection['capital_nature'][cnt_y] = investment
                    data_collection['co2_investment'][cnt_y] = [investment]
                    data_collection['share_of_co2_investment'][cnt_y] = [investment/data_collection['capital_total'][cnt_y]]

            if cnt_y in data_collection['capital_total'] and cnt_y-1 in data_collection['capital_total']:
                data_collection['delta_capital'][cnt_y] = data_collection['capital_total'][cnt_y] - data_collection['capital_total'][cnt_y-1]
                data_collection['delta_capital_pi_base'][cnt_y] = [data_collection['delta_capital'][cnt_y]]
            if cnt_y in data_collection['capital_nature'] and (cnt_y-1) in data_collection['capital_nature']:
                data_collection['delta_capital_nature'][cnt_y] = [data_collection['co2_investment'][cnt_y][-1] - data_collection['co2_investment'][cnt_y-1][-1]]


            cnt_y+=1

        data_collection['business_power']       = self.__calc_business_power(data_collection['gdp'], data_collection['delta_capital'])
        data_collection['delta_market_condition_pi'], data_collection['market_conditions']    = self.__calc_market_conditions(data_collection['delta_gdp'], data_collection['total_assets'])

        data_collection['market_conditions_nature']     = self.__calc_market_conditions_nature(data_collection['delta_co2_consumption'], data_collection['capital_nature'])
        data_collection['nature_power']                 = self.__calc_nature_power(data_collection['co2_consumption'], data_collection['delta_capital_nature'])

        #Create simulation base
        data_collection['business_power_pi']            = self.create_sim_base(data_collection['business_power'])
        data_collection['business_value_share_pi']      = self.create_sim_base(data_collection['share_of_gdp'])
        data_collection['capital_share_pi']             = self.create_sim_base(data_collection['share_of_total_assets'])
        data_collection['delta_co2_consumption_pi']     = self.create_sim_base(data_collection['delta_co2_consumption'])
        data_collection['delta_co2_price_pi']           = self.create_sim_base(data_collection['delta_co2_price_pi_base'])

        data_collection['delta_co2_intensity_pi']       = self.create_sim_base(data_collection['delta_co2_intensity'])

        data_collection['co2_investment_share_pi']      = self.create_sim_base(data_collection['share_of_co2_investment'])
        data_collection['delta_capital_nature_pi']      = self.create_sim_base(data_collection['delta_capital_nature'])
        data_collection['delta_carbon_credits_pi']      = self.create_sim_base(data_collection['delta_carbon_credits'])
        data_collection['delta_co2_emission_global_pi'] = self.create_sim_base(data_collection['delta_co2_emission_global'])
        data_collection['delta_gdp_pi']                 = self.create_sim_base(data_collection['delta_gdp_pi_base'])
        data_collection['delta_capital_pi']             = self.create_sim_base(data_collection['delta_capital_pi_base'])

        data_collection['grow_rate_pi']                 = self.create_sim_base(data_collection['grow_rate'])
        data_collection['delta_co2_subvention_pi']      = self.create_sim_base(data_collection['delta_co2_subvention'])
        data_collection['delta_free_allowances_pi']     = self.create_sim_base(data_collection['delta_free_allowances'])
        data_collection['delta_sale_allowances_pi']     = self.create_sim_base(data_collection['delta_sale_allowances'])
        data_collection['nature_power_pi']              = self.create_sim_base(data_collection['nature_power'])


        data_collection['price_credit'] = self.__simulate_credit_price_history(data_collection["price_credit"],1990, 2023)
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
                                start_capital_business,
                                start_capital_total,
                                capital_business_share_start,
                                delta_co2_emission_global_pi,
                                delta_gdp_pi,
                                delta_market_condition_pi,
                                co2_emission_global_start,
                                start_delta_business_value,
                                co2_investment_share_pi,
                                gdp_start,
                                market_condition_pi,
                                year
                                ):
        general_market = MarketGeneral(self.assume,
                                       business_power_pi,
                                       business_value_share_start,
                                       start_capital_business,
                                       start_capital_total,
                                       capital_business_share_start,
                                       delta_co2_emission_global_pi,
                                       delta_gdp_pi,
                                       delta_market_condition_pi,
                                       co2_emission_global_start,
                                       start_delta_business_value,
                                       co2_investment_share_pi,
                                       gdp_start,
                                       market_condition_pi
                                       )

        company_list = self.__create_company_list(general_market,year)

        return company_list, general_market

    def __create_company_list(self, general_market,year):
        cnt_com=0
        com_list = {}
        while cnt_com<self.number_companies:
            business_value_start, capital_start, capital_nature_start, delta_business_value_start, journal= general_market.sim_start_of_company(self.number_companies,year)
            company = Company(business_value_start, capital_start, capital_nature_start, delta_business_value_start)
            company.journal = journal
            company.business_power, company.is_alive, company.market_influence = general_market.sim_company_situation(company)
            com_list[cnt_com] = company
            cnt_com+= 1
        general_market.count_company = self.number_companies
        general_market.sim_start_rest_of_the_world(com_list)
        return com_list

    def __create_co2_market(self,
                            state_of_atmosphere_start,
                            capital_nature_start,
                            carbon_credit_supply_start,
                            co2_consumption_start,
                            co2_emission_big_share_start,
                            co2_emission_total_start,
                            co2_emission_sum_start,
                            co2_intensity_start,
                            co2_subvention_start,
                            company_list,
                            delta_capital_nature_pi,
                            delta_carbon_credits_supply_pi,
                            delta_co2_consumption_pi,
                            delta_co2_intensity_pi,
                            delta_co2_price_pi,
                            delta_co2_subvention_pi,
                            delta_free_allowances_pi,
                            delta_sale_allowances_pi,
                            free_allowances_start,
                            price_allowances_start,
                            price_credit_start,
                            rest_of_the_world,
                            share_of_idle
                            ):
        co2_market = MarketCo2(self.assume,
                               state_of_atmosphere_start,
                               capital_nature_start,
                               carbon_credit_supply_start,
                               co2_consumption_start,
                               co2_emission_sum_start,
                               co2_intensity_start,
                               co2_subvention_start,
                               delta_capital_nature_pi,
                               delta_carbon_credits_supply_pi,
                               delta_co2_consumption_pi,
                               delta_co2_intensity_pi,
                               delta_co2_price_pi,
                               delta_co2_subvention_pi,
                               delta_free_allowances_pi,
                               delta_sale_allowances_pi,
                               free_allowances_start,
                               price_allowances_start,
                               price_credit_start,
                                                           )
        #rest_of_the_world.co2_emission = co2_emission_total_start - co2_emission_sum_start
        co2_market.sim_start_of_company(company_list, rest_of_the_world, co2_emission_total_start, co2_emission_sum_start)

        return co2_market

    def __calc_eco_performance(self, co2_em, co2_consumption, state_of_atmosphere_last_year):
        #https://wiki.bildungsserver.de/klimawandel/index.php/Kohlendioxid-Konzentration
        #  1 ppm CO2 = 7,814 Gt CO2
        # co2_em and co2_consumption given in Gt CO2
        r_factor = 7.814

        v_co2 = co2_em / r_factor ## change of atmospheric state by human impact in ppm
        c_co2 = co2_consumption / r_factor
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
        dead_list = {}
        company_list, general_market = self.__create_general_market(
            self.mc_data['business_power_pi'],
            self.mc_data['share_of_gdp'][self.start_year][-1],
            self.mc_data['capital_business'][self.start_year],
            self.mc_data['capital_total'][self.start_year],
            self.mc_data['share_of_total_assets'][self.start_year][-1],
            self.mc_data['delta_co2_emission_global_pi'],
            self.mc_data['delta_gdp_pi'],
            self.mc_data['delta_market_condition_pi'],
            self.mc_data['co2_emission_global'][self.start_year],
            self.mc_data['delta_gdp'][self.start_year],
            self.mc_data['co2_investment_share_pi'],
            self.mc_data['gdp'][self.start_year],
            self.mc_data['market_conditions_pi'],
            self.start_year
        )

        max_id = max(company_list.keys())

        co2_market = self.__create_co2_market(  self.mc_data['state_of_atmosphere'][self.start_year],
                                                self.mc_data['capital_nature'][self.start_year],
                                                self.mc_data['carbon_credits'][self.start_year],
                                                self.mc_data['co2_consumption'][self.start_year],
                                                self.assume['share_of_co2'],
                                                self.mc_data['co2_emission_global'][self.start_year],
                                                self.mc_data['co2_emission_sum'][self.start_year],
                                                self.mc_data['co2_intensity'][self.start_year],
                                                self.mc_data['co2_subvention'][self.start_year],
                                                company_list,
                                                self.mc_data['delta_capital_nature_pi'],
                                                self.mc_data['delta_carbon_credits_pi'],
                                                self.mc_data['delta_co2_consumption_pi'],
                                                self.mc_data['delta_co2_intensity_pi'],
                                                self.mc_data['delta_co2_price_pi'],
                                                self.mc_data['delta_co2_subvention_pi'],
                                                self.mc_data['delta_free_allowances_pi'],
                                                self.mc_data['delta_sale_allowances_pi'],
                                                self.mc_data['free_allowances'][self.start_year],
                                                self.mc_data['price_allowances'][self.start_year],
                                                self.mc_data['price_credit'][self.start_year],
                                                general_market.rest_of_the_world,
                                                self.assume['share_of_idle']
                                                )
        year = self.start_year
        while year < self.target_year:
            ### simulate
            progress_counter +=1
            self.__simulate_market_and_choose_company_options(company_list, co2_market, general_market, year)
            company_list, dead_list, max_id = self.__check_surviver(company_list, dead_list, general_market)




            #############################grant free allowances##############################################
            ##INPUT: company.co2_apply_free, co2_market.free_allowances
            #self.__authorize_free_allowances(co2_market,company_list)
            ##OUTPUT: company.co2_demand
            #############################Sale Allowances##############################################
            ##INPUT: company.co2_demand
            #self.__trade_allowances(co2_market, company_list)
            #############################Voluntary Carbon Market##############################################
            #volunteer = [company_list[index] for index in company_list if not company_list[index].is_co2_taxable]
            #self.__trade_carbon_voluntarily(volunteer, co2_market)
            #############################taxes##############################################
            #taxables = [company_list[index] for index in company_list if company_list[index].is_co2_taxable]
            #self.__collect_taxes(co2_market, taxables, year)

            #self.__make_saldo_nature(company_list, co2_market)


            ## log all infos
            co2_market.log_to_journal(year)
            general_market.log_to_journal(year)

            ### for progress check on long runs
            if progress_counter % 10 == 0:
                total = (self.target_year-self.start_year)
                print("Trial: {0} Progress: {1} %".format(trials_id, round(100*progress_counter/total,2)))

            year += 1

            #self.__new_participants(company_list, co2_market, general_market, max_id, year)
        mc_result={

            'company_list'  : company_list,
            'co2_market'    : co2_market,
            'dead_list'     : dead_list,
            'general_market': general_market
        }
        return mc_result
    def __simulate_internal_decision_slim(self, company_list, co2_market, general_market, year):
        #1. Das Verfügbare Kapital Aus den Vorjahres Daten ermitteln

        #2. Simulation der volatilen parameter market_condition, business_power und preis_co2
        #3. budget verteilung
        #4. Berechnung Jahresabschluss
        return

    def __simulate_market_and_choose_company_options(self, company_list, co2_market, general_market, year):
        ###1. Sim general market
        general_market.count_company = len(company_list)
        general_market.sim_new_year()
        co2_market.sim_new_year_co2(general_market.co2_emission_global)
        general_market.rest_of_the_world.capital_nature = 0
        general_market.calc_co2_emission_row()
        self.__run_row_market_status(general_market)

        sum_co2_emission = 0
        sum_capital_business = general_market.rest_of_the_world.capital_business
        sum_capital_nature = 0
        sum_business_value = 0
        sum_capital_total = general_market.rest_of_the_world.capital

        for index in company_list:
            company=company_list[index]
            ##set market boost and co2_intensity
            #self.__calc_company_collect_payout(company, general_market)

            ##2. choose options
            #calc available capital for this year
            #self.__run_company_annual_financial_status(company,general_market)
            #3. simulate options effect

            #self.__run_company_budget_planning_scenario_one(company,co2_market, general_market)
            #self.__run_company_business_scenario_one(company, general_market)
            #self.__run_company_annual_nature_status_scenario_one(co2_market, company)


            business_power = company.business_power
            capital_ly = company.capital
            delta_capital_ly = company.delta_capital
            delta_market_influence_ly = company.delta_market_influence  #individual
            market_influence_ly = company.market_influence

            #evaluate company situation
            (business_power,
             capital,
             market_influence) = general_market.sim_company_start_year(business_power,
                                                                       capital_ly,
                                                                       delta_capital_ly,
                                                                       delta_market_influence_ly,
                                                                       market_influence_ly)

            #base data:
            volunteer = not company.is_co2_taxable
            co2_emission_ly = company.co2_emission
            co2_price = co2_market.co2_price
            business_value_ly = company.business_value
            delta_market_influence = 0


            #handlungsoption und handlungswirkung
            (budget_marketing,
             budget_technology,
             capital_business,
             capital_nature,
             co2_intensity,
             delta_market_influence) = self.__sim_company_budget_choice_sc1(co2_market,
                                                                            company,
                                                                            general_market
                                                                            )


            ##Calculation
            (business_value,
             capital_nature,
             co2_emission,
             delta_capital_business,
             delta_capital_nature,
             income) = self.__calc_company_state_sc1(business_power,
                                                     business_value_ly,
                                                     budget_marketing,
                                                     capital_business,
                                                     co2_emission_ly,
                                                     co2_price,
                                                     co2_intensity,
                                                     market_influence,
                                                     capital_nature,
                                                     volunteer)


            #write back zu company object
            company.business_power = business_power
            company.business_value = business_value
            company.capital_business = capital_business
            company.capital_nature = capital_nature
            company.co2_emission = co2_emission
            company.co2_intensity = company.co2_emission/company.business_value #not kumulativ
            company.delta_capital = income
            company.delta_capital_business = delta_capital_business
            #company.delta_co2_intensity = delta_co2_intensity
            company.delta_market_influence = delta_market_influence

            company.log_to_journal(year)

            sum_business_value  += company.business_value
            sum_capital_total   += company.capital
            sum_capital_business+= company.capital_business
            sum_co2_emission    += company.co2_emission #in  mio metric tons
            sum_capital_nature  += company.capital_nature

        sum_gdp = sum_business_value + general_market.rest_of_the_world.business_value
        co2_emission_global = sum_co2_emission + general_market.rest_of_the_world.co2_emission



        ###4. calc general market
        general_market.capital_total       = sum_capital_total
        general_market.capital_business    = sum_capital_business
        general_market.gdp                 = sum_gdp
        general_market.business_value_sum  = sum_business_value
        general_market.co2_emission_global = co2_emission_global

        ###5. calc co2 market
        co2_market.co2_emission_sum = sum_co2_emission #sum partizipants
        co2_market.total_capital_nature = sum_capital_nature #sum partizipant and rest of the world
        co2_market.co2_intensity = co2_market.co2_emission_sum / sum_business_value

        return

    #def __authorize_free_allowances(self, co2_market, company_list):
    #    cscf = co2_market.calc_cross_sectoral_correction_factor()
    #    sum_demand_sale = 0
    #    sum_granted_free = 0
    #    for index in company_list:
    #        company = company_list[index]
    #        if company.is_applying:
    #            free_co2 = company.co2_emission * cscf
    #            co2_market.invoice['free'].append((company, co2_market, 0.0, free_co2))
    #            company.co2_demand = company.co2_emission - free_co2
    #            sum_demand_sale  += company.co2_demand
    #            sum_granted_free += free_co2
    #    co2_market.demand_sale_sum = sum_demand_sale
    #    co2_market.granted_free_sum = sum_granted_free
    #    return

    #def __trade_allowances(self, co2_market, company_list):
    #    demander_list = co2_market.price_finding_to_sale_allowances(company_list)
    #    sold_allowances = 0
    #    demander_with_remaining_stock = []
    #    sum_remaining_stock = 0
    #    while co2_market.sale_allowances_supply > sold_allowances and len(demander_list) > 0:

    #        id = random.randint(-1 , len(demander_list)-1)
    #        demander = demander_list[id]
    #        decrease = 0
    #        if (demander.co2_demand + sold_allowances) <= co2_market.sale_allowances_supply:
    #            sold_allowances += demander.co2_demand
    #            decrease = demander.co2_demand
    #        else:
    #            decrease = co2_market.sale_allowances_supply - sold_allowances

    #        price = decrease * co2_market.price_allowances

    #        if price < demander.capital_nature:
    #            demander.co2_demand -= decrease
    #            demander.capital_nature -= price
    #            sold_allowances += decrease
    #            co2_market.invoice['sale'].append((demander, co2_market, decrease, price))
    #        else:
    #            demander_with_remaining_stock.append(demander)
    #            sum_remaining_stock += demander.co2_remaining_stock

    #        demander_list.remove(demander)
    #    co2_market.sold_allowances_sum = sold_allowances
    #    co2_market.remaining_stock_sum = sum_remaining_stock
    #    return

    #def __trade_carbon_voluntarily(self, demander, co2_market):
    #    ## SET mi if demander co2_remaining_stock ==0
    #    credit_supply = co2_market.carbon_credit_supply ## EINHEIT ????
    #    price = co2_market.price_credit
    #    sum_carbon_credit = 0
    #    for company in demander:
    #        carbon_amount = company.co2_remaining_stock
    #        price_credit = carbon_amount*price
    #        if credit_supply >=carbon_amount:
    #            co2_market.invoice['vcm'] = (company, co2_market, price_credit, carbon_amount)
    #            credit_supply -= carbon_amount
    #            sum_carbon_credit += carbon_amount

    #            company.capital_nature -= price_credit
    #            if company.co2_remaining_stock == 0:
    #                company.market_influence += 0.3

    #    co2_market.carbon_credit_sum = sum_carbon_credit

    #    return
    #def __collect_taxes(self, co2_market, company_list, year):
    #    total_taxes = 0
    #    for index in company_list:
    #        company = company_list[index]
    #        amount = company.co2_remaining_stock
    #        tax = co2_market.get_tax_price_per_mio_metric_ton(year) * amount
    #        co2_market.invoice['tax'] = (company, co2_market, tax, amount)
    #        company.log_to_journal(year)
    #        total_taxes += tax
    #    return total_taxes
    #def __make_saldo_nature(self, company_list, co2_market):
        #sum_delta_capital_nature = 0
    #    for index in company_list:
    #        company = company_list[index]
    #        company.saldo_nature = co2_market.calc_company_nature_saldo(company)
            #sum_delta_capital_nature += company.saldo_nature
        #co2_market.delta_capital_nature_sum =sum_delta_capital_nature

    def __new_participants(self,company_list, co2_market, general_market, max_id, year):
        mu = mean(self.mc_data['grow_rate_pi'])
        sigma = stdev(self.mc_data['grow_rate_pi'])
        grow_rate = random.gauss(mu, sigma)

        if grow_rate > 0:
            number_new = int(round(grow_rate * len(company_list), 0))
            index = 0
            while index<number_new:
                business_value, capital, capital_nature, delta_business_value, journal = general_market.sim_start_of_company(number_new+len(company_list), year)
                company = Company(business_value, capital, capital_nature, delta_business_value)
                company.journal = journal
                general_market.rest_of_the_world.business_value -= business_value
                general_market.rest_of_the_world.capital -= capital

                co2_market.sim_entrance_new_company(company, len(company_list), general_market.rest_of_the_world)

                index += 1
                company_list[max_id+index] = company
        general_market.count_company = len(company_list)


        #co2_market.sim_start_of_company(company_list, general_market.rest_of_the_world, general_market.co2_emission_total_start, co2_emission_sum_new)

        return
    def __check_surviver(self,company_list, dead_list, general_market):
        new_company_list = {}
        for id, company in company_list.items():
            #company = company_list[index]
            if company.is_alive:
                new_company_list[id] = company
            else:
                dead_list[id] = company
                general_market.rest_of_the_world.business_value += company.business_value
                general_market.rest_of_the_world.capital += company.capital
                general_market.rest_of_the_world.co2_emission += company.co2_emission
        max_id_alive = max(new_company_list.keys())
        if len(dead_list) == 0:
            max_id_dead = 0
            #return 0 as max value in case dead_list is empty
        else:
            max_id_dead = max(dead_list.keys())

        max_id = max(max_id_alive, max_id_dead)
        return new_company_list, dead_list, max_id

    def __run_company_business_scenario_one(self,company,  general_market):

        company.business_power = company.delta_business_power
        ## calc business value
        business_value_last_year = company.business_value
        capital_business = company.capital_business
        market_influence = company.market_influence
        company.business_value, company.delta_business_value = general_market.calc_company_business_value(business_value_last_year,
                                                                                                          capital_business,
                                                                                                          market_influence)
        return

        #co2 emissionen berechnen
        #company.co2_emission = co2_market.calc_company_co2_emission(company.business_value, company.co2_intensity)
        #co2 costen berechnen

    def __company_use_budget(self, company, co2_market, general_market):
        #Option 1 Investition in technologie
        #Option 2 Investition in CO2Markt
        price_limit_co2 = company.budget_to_pay_off_emissions/company.co2_emission
        ## SET bp
        #budget = company.budget_to_improve[0]
        #business_power_last_year = company.business_power
        #business_value_last_year = company.business_value
        #company.business_power = general_market.company_option_improve_business_power(budget,business_power_last_year, business_value_last_year)


        ## SET nature power
        #budget = company.budget_to_improve[1]
        #co2_market.company_option_improve_nature_power(budget, company)

        ## SET co2intensity,
        #budget = company.budget_to_improve[2]
        #co2_intensity_last_year = company.co2_intensity
        #company.co2_intensity = co2_market.company_option_improve_co2_intensity(budget, co2_intensity_last_year)

        ## SET business power down to apply free allowances
        #budget = company.budget_to_improve[3]
        #co2_market.company_option_apply_free_allowances(budget, company)
    def __calc_company_state_sc1(self, business_power,
                                 business_value_ly,
                                 budget_marketing,
                                 capital_business,
                                 co2_emission_ly,
                                 co2_price,
                                 co2_intensity,
                                 market_influence,
                                 capital_nature,
                                 volunteer):
        delta_business_value = capital_business * market_influence
        #delta_co2_emission = delta_business_value * delta_co2_intensity
        #print("delta_co2_intensity",delta_co2_intensity)
        #print("delta_business_value",delta_business_value)
        #diff = delta_co2_intensity**2 - delta_business_value**2
        #if diff < 0:
        #    delta_co2_emission = -1 *math.sqrt(abs(diff)) #Pythagoras
        #else:
        #    delta_co2_emission = math.sqrt(diff) #Pythagoras
        #co2_emission = co2_emission_ly + delta_co2_emission

        business_value = business_value_ly + delta_business_value
        co2_emission = co2_intensity*business_value
        delta_capital_business = business_value *business_power
        cost_emission = co2_price * co2_emission
        if volunteer and budget_marketing<cost_emission:
            cost_emission = budget_marketing

        delta_capital_nature = -1 * cost_emission
        capital_nature = capital_nature + delta_capital_nature
        income = delta_capital_business + delta_capital_nature
        return business_value, capital_nature, co2_emission, delta_capital_business, delta_capital_nature, income

    def __sim_company_budget_choice_sc1(self, co2_market, company, general_market):
        capital = company.capital
        is_volunteer = not company.is_co2_taxable
        co2_intensity_ly = company.co2_intensity

        share_mark_invest = general_market.sim_share_mark_invest()
        share_tech_invest = general_market.sim_share_tech_invest()
        budget_marketing = capital * share_mark_invest
        budget_technology = capital * share_tech_invest
        capital_business = capital - budget_marketing - budget_technology
        capital_nature = 0
        delta_market_influence = 0

        co2_intensity = co2_market.sim_company_co2_intensity(co2_intensity_ly)#TO DO: random by budget
        if is_volunteer:
            delta_market_influence = general_market.sim_company_delta_market_influence() #TO DO: random if budget ok
        return budget_marketing, budget_technology, capital_business, capital_nature, co2_intensity, delta_market_influence

    def __run_company_budget_planning_scenario_one(self, company,co2_market, general_market):
        sim_investment_share = general_market.sim_investment_share()
        investment = company.capital * sim_investment_share
        #Option 1 Investition in technologie
        budget_to_improve_co2_intensity = investment * random.random()
        #Auszahlung wird hier für das nächste jahr generiert
        delta_co2_intensity = co2_market.sim_company_delta_co2_intensity(budget_to_improve_co2_intensity)
        company.delta_co2_intensity_history.append(delta_co2_intensity)
        #Option 2 Investition in CO2 Markt
        budget_limit_to_pay_off_emissions = investment - budget_to_improve_co2_intensity
        #company.\
        delta_market_influence = general_market.sim_market_influence(budget_limit_to_pay_off_emissions, company.market_influence)
        capital_nature = 0 #not existent in scenario 1
        #obligatorisch Kapital für betriebliche Leistungen
        company.capital_business = company.capital - investment



        #just for journaling
        company.budget_to_improve=(
            budget_to_improve_co2_intensity,
            budget_limit_to_pay_off_emissions
        )
        return

    def __run_company_budget_planning_scenario_two(self, company,year):
        #Option 1 Investition in technologie
        budget_to_improve_co2_intensity = company.capital * 0.1 #TODO wieviel und warum
        #Option 2 Investition in CO2 Markt
        budget_limit_to_pay_off_emissions = company.capital *0.1
        #Option 3 Kapital für ökologische Leistungen
        capital_nature = company.capital * 0.1 #TODO wieviel und warum
        #obligatorisch Kapital für betriebliche Leistungen
        company.capital_business = company.capital - budget_to_improve_co2_intensity - capital_nature
        company.budget_to_improve = (
            budget_to_improve_co2_intensity,
            budget_limit_to_pay_off_emissions,
        )
        return

        ## split capital to business and nature purpose
        ## SET Budget for bp, np, co2idle, free_allowances, buy_allowances
        #budget_to_improve_business_power = company.capital * 0.01 # TO DO wieviel und warum
        #company.capital_nature = company.capital * 0.2

        #capital_business = company.capital_business
        #capital_nature =  company.capital_nature

        ###4. budget planning to improve performance

        #share_to_improve_business_power = 0.1
        #share_to_improve_nature_power = 0.1
        #share_to_improve_co2_emission_idle = 0.1
        #share_to_improve_apply_free_allowances = 0.1
        #share_to_improve_buy_allowances = 0.7
        #capital_nature     -= share_to_improve_nature_power * company.capital_nature
        #capital_nature     -= share_to_improve_apply_free_allowances * company.capital_nature
        #capital_nature     -= share_to_improve_buy_allowances * company.capital_nature
        #budget_to_improve_bp = 0
        #budget_to_improve_intensity = 0

        #if 'business_power' in company.journal[year-2]:
        #    delta_bp_last_year = company.journal[year-2]['business_power'] - company.journal[year-1]['business_power']
        #    budget_to_improve_bp = delta_bp_last_year * company.capital_business
        #if 'co2_intensity' in company.journal[year-2]:
        #    delta_co2_intensity = company.journal[year-2]['co2_intensity'] - company.journal[year-1]['co2_intensity']
        #    budget_to_improve_intensity = delta_co2_intensity * company.capital_nature

        #capital_business    -= budget_to_improve_bp
        #capital_nature      -= budget_to_improve_intensity

        #budget_to_improve = (budget_to_improve_bp,
        #                     0,
        #                     budget_to_improve_intensity,
        #                     0,
        #                     0)
        #company.budget_to_improve = budget_to_improve
        #company.capital_business = capital_business
        #company.capital_nature = capital_nature

    def __calc_company_collect_payout(self, company, general_market):

        ## set market_influence by general market and market boost
        # general_market.delta_market_condition +
        company.market_influence += company.delta_market_influence
        company.co2_intensity += company.delta_co2_intensity
        return

    def __run_row_market_status(self, general_market):
        company = general_market.rest_of_the_world
        business_value_last_year = company.business_value
        capital_last_year = company.capital_business
        ###2. sim general_market conditions for this single company
        company.business_power, company.is_alive, company.market_influence = general_market.sim_company_situation(company)

        ###3. calc company status related to general market conditions
        general_market.calc_row_situation()


    def __run_company_annual_financial_status(self, company, general_market):
        company.capital = company.capital_business + company.capital_nature

        business_power_last_year = company.business_power
        business_value_last_year = company.business_value
        capital_last_year = company.capital_business

        ### SET capital, delta_capital=income_business and is_alive
        company.capital_business, company.delta_capital = general_market.calc_company_capital(
            business_power_last_year,
            business_value_last_year,
            capital_last_year)
        company.is_alive = general_market.check_company_if_survived(company)


    def __run_company_annual_nature_status_scenario_one(self, co2_market, company):
        delta_business_value        = company.delta_business_value
        business_value              = company.business_value
        co2_emission_last_year      = company.co2_emission
        co2_intensity               = company.co2_intensity
        budget_to_improve_co2_intensity = company.budget_to_improve[0]

        company.co2_emission = co2_market.calc_company_technical_improvement(
            budget_to_improve_co2_intensity,
            business_value,
            delta_business_value,
            co2_emission_last_year,
            co2_intensity,
        )
        return

        #budget_to_pay_off_emissions=company.budget_to_improve[1]
        #co2_emission = company.co2_emission
        #is_co2_taxable = company.is_co2_taxable

        #delta_market_influence, overshoot = co2_market.calc_company_marketing_improvement(budget_to_pay_off_emissions, co2_emission, is_co2_taxable)
        #company.capital_business += overshoot
        #company.delta_market_influence = delta_market_influence
    #capital_nature_last_year    = company.capital_nature
    #co2_consumption_last_year   = company.co2_consumption
    #co2_correlation_factor      = company.co2_correlation_factor
    #co2_subvention_last_year    = company.co2_subvention
    #market_influence_nature     = company.market_influence_nature
    #nature_power                = company.nature_power

    ## calc co2_consumptions
    #(company.capital_nature,
    # company.co2_apply_free,
    # company.co2_consumption,
    #capital_nature_last_year,
    #co2_consumption_last_year,
    #co2_correlation_factor,
    #co2_subvention_last_year,
    #company,
    #market_influence_nature,
    #nature_power
    # company.co2_supply) =

    def __optimize_capital_nature(self,
                                  price,
                                  capital_total,
                                  gdp_last_year,
                                  market_condition,
                                  ):
        mk_p = market_condition*price
        cap_gdp = 2* gdp_last_year*capital_total*self.a

        term_1 = mk_p / cap_gdp
        term_2 = self.b / (2* self.a * capital_total)

        return term_1-term_2 *capital_total

    def create_sim_base(self, data_to_sim):
        pi = []
        for key in data_to_sim:
            if len(data_to_sim[key])>0:
                pi.append(data_to_sim[key][-1])
        return pi
    def __simulate_credit_price_history(self, data, start, end):

        sim_base = []
        old_key = -1
        for key in data:
            if old_key in data:
                delta_value = data[key] - data[old_key]
                sim_base.append(delta_value)
            old_key = key

        year = min (data.keys())
        while year < end:
            if not year in data and (year-1) in data:
                sim_value = -1
                while sim_value < 0:
                    #sim value
                    mu = mean(sim_base)
                    sigma = stdev(sim_base)
                    delta_value = random.gauss(mu,sigma)
                    sim_value = data[year-1] + delta_value
                data[year] = sim_value
            year+= 1

        year = min(data.keys())
        while year > start:

            if not year in data and (year+1) in data:
                sim_value = -1
                delta_value = 0
                while sim_value < 0:
                    #sim value
                    mu = mean(sim_base)
                    sigma = stdev(sim_base)
                    delta_value = random.gauss(mu,sigma)
                    sim_value = data[year+1] - delta_value
                sim_base.append(delta_value)
                data[year] = sim_value
            year-= 1

        return  data
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
        delta_mc_pi=[]
        for year in data_delta_gdp:
            if year in data_total_assets:
                if not year in m_cond:
                    m_cond[year] = []
                m_cond[year].append(data_delta_gdp[year] / data_total_assets[year])
                if year-1 in m_cond:
                    delta_mc = m_cond[year][0] - m_cond[year-1][0]
                    delta_mc_pi.append(delta_mc)
        return delta_mc_pi, m_cond
    def __calc_nature_power(self, data_nature_value, data_delta_capital_nature):
        nature_power = {}
        for year in data_delta_capital_nature:
            if not year in nature_power:
                nature_power[year] = []
            if year-1 in data_nature_value:
                if not year-1 in nature_power:
                    nature_power[year-1] = []
                if data_nature_value[year-1] == 0:
                    nature_power[year-1].append(0)
                else:
                    nature_power[year-1].append(data_delta_capital_nature[year][-1]/data_nature_value[year-1])
        return nature_power

    def __calc_market_conditions_nature(self,data_delta_nature_value,data_capital_nature):

        m_cond = {}
        for year in data_delta_nature_value:
            if year in data_capital_nature:
                if not year in m_cond:
                    m_cond[year] = []
                m_cond[year].append(data_delta_nature_value[year][-1] / data_capital_nature[year])
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


    def plot_results(self, mc_result, csv_service):


        self.plot_data = mc_result

        # plot_labels legend
        # [0] = market
        # [1] = name of plot file and title
        # [2] = label in data
        # [3] = label in scenarios
        # [4] = unit

        plot_labels = [
            ('general_market', 'capital_business', 'total_assets', 'capital_business', 'in Mrd Euro'),
            ('general_market', 'capital_total', 'capital_total', 'capital_total', 'in Mrd Euro'),
            ('general_market', 'Co2_Emission_global', 'co2_emission_global', 'co2_emission_global','mio metric tones Co2 Emission'),

            ('general_market', 'Count_company', '', 'count_company','number of surviving companies'),
            ('general_market', 'gdp', 'gdp', 'gdp', 'in Mrd Euro'),
            ('general_market', 'GDP_Participants', 'business_values', 'business_value_sum', 'in Mrd Euro'),

            #('co2_market', 'capital_nature', 'capital_nature', 'capital_nature_sum','mrd Euro'),

            ('co2_market', 'Co2_Emission_sum', 'co2_emission_sum', 'co2_emission_sum','mio metric tones CO2 Emission'),
            ('co2_market', 'Co2_Intensity', 'co2_intensity', 'co2_intensity','mio metric tones CO2 Emission equivalence per Mrd Euro'),
            ('co2_market', 'State_of_Atmosphere', 'state_of_atmosphere', 'state_of_atmosphere','ppm CO2'),
            ('co2_market', 'Co2_consumption', 'co2_consumption', 'co2_consumption','mio metric tones CO2 natural consumption'),
        ]
        self.csv_service = csv_service
        #self.transform_data_and_plot(
        #    ('general_market', 'GDP Participants', 'business_values', 'business_value_sum', 'in Mrd Euro'),
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
        self.csv_service.save_mc_result_sim4(data, tuple, self.start_year, self.target_year, self.end_time.strftime('%Y%m%d_%H%M'))
        return data



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
