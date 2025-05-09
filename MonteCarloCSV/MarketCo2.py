import random
import math
from statistics import mean, stdev

import numpy as np
from mesonbuild.scripts.env2mfile import detect_missing_native_binaries


class MarketCo2:
    def __init__(self, assume,
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
                 delta_free_allowance_supply_pi,
                 delta_sale_allowance_supply_pi,
                 free_allowances_supply_start,
                 price_allowances_start,
                 price_credit_start
                 ):
        self.__assume = assume
        #self.__delta_co2_subvention_pi      = delta_co2_subvention_pi
        #self.__delta_capital_nature_pi      = delta_capital_nature_pi
        #self.__delta_free_allowances_pi     = delta_free_allowance_supply_pi
        #self.__delta_sale_allowances_pi     = delta_sale_allowance_supply_pi
        #self.__delta_carbon_credits_pi      = delta_carbon_credits_supply_pi

        #self.free_allowances_supply    = free_allowances_supply_start
        #self.sale_allowances_supply    = sale_allowances_supply_start
        #self.carbon_credit_supply      = carbon_credit_supply_start
        #self.apply_free_sum            = 0
        #self.demand_sale_sum           = 0
        #self.remaining_stock_sum       = 0

        #self.__cross_sectoral_correction_factor = free_allowances_supply_start / co2_emission_sum_start
        #self.price_allowances          = price_allowances_start
        #self.price_credit              = price_credit_start
        self.price_co2 = price_credit_start
        self.delta_co2_price_pi = delta_co2_price_pi
        self.price_ppm = self.__calc_impact_price(self.price_co2, state_of_atmosphere_start)
        #self.granted_free_sum              = 0
        #self.sold_allowances_sum           = 0
        #self.carbon_credit_sum             = 0
        self.co2_consumption            = co2_consumption_start
        self.__delta_co2_consumption_pi   = delta_co2_consumption_pi
        self.co2_emission_sum           = co2_emission_sum_start
        self.co2_intensity              = co2_intensity_start
        self.__delta_co2_intensity_pi    = delta_co2_intensity_pi
        #self.co2_subvention             = co2_subvention_start
        self.capital_nature_sum         = capital_nature_start
        self.delta_capital_nature_sum   = 0

        #self.delta_carbon_credits_supply = self.__sim_delta_carbon_credits_supply()

        #self.delta_co2_subvention = self.__sim_delta_co2_subvention()
        #self.delta_free_allowances = self.__sim_delta_free_allowances_supply()
        #self.delta_sale_allowances = self.__sim_delta_sale_allowances_supply()

        self.state_of_atmosphere = state_of_atmosphere_start

        #self.invoice = {
            #           (Demander, Supplier, Sales price, tCo2)
       #     'free' : [(None,None,0.0,0.0)],
       #     'sale' : [(None,None,0.0,0.0)],
       #     'vcm'  : [(None,None,0.0,0.0)],
       #     'tax'  : [(None,None,0.0,0.0)]
       # }
        self.journal={
            -1: {
                'state_of_atmosphere' :        float(self.state_of_atmosphere),
                'capital_nature_sum':          float(self.capital_nature_sum),
                'co2_consumption'     :        float(self.co2_consumption),
                'co2_emission_sum':            float(self.co2_emission_sum),
                'co2_intensity':               float(self.co2_intensity),
                #'co2_subvention':              float(self.co2_subvention),
                #'free_allowances_supply':      float(self.free_allowances_supply),
                #'granted_free_sum':            float(self.granted_free_sum),
                #'invoice':                           self.invoice,
                #'sale_allowances_supply':      float(self.sale_allowances_supply),
                #'sold_allowances_sum':         float(self.sold_allowances_sum),
                #'remaining_stock_sum':         float(self.remaining_stock_sum),
            }
        }

        self.co2_balance = 0
        return

    def sim_new_year_co2(self, co2_emission_global_ly):
        self.state_of_atmosphere = self.__calc_new_state_of_atmosphere(self.state_of_atmosphere,self.co2_consumption, co2_emission_global_ly)
        delta_co2_consumption = self.__sim_delta_co2_consumption()
        co2_consumption = self.co2_consumption + delta_co2_consumption
        if co2_consumption < 0:
            co2_consumption = 0
            #print ("detected 0 consumption this year")
        self.co2_consumption = co2_consumption
        self.co2_price = self.__sim_co2_price()

        return

    def __sim_co2_price(self):
        mu = mean(self.delta_co2_price_pi)
        sigma = stdev(self.delta_co2_price_pi)
        delta_co2_price = random.gauss(mu, sigma)
        self.delta_co2_price_pi.append(delta_co2_price)

        co2_price = self.price_co2 + delta_co2_price
        return co2_price


        #(self.capital_nature)



        #self.delta_free_allowances = self.__sim_delta_free_allowances_supply()
        #self.free_allowances_supply = self.free_allowances_supply + self.delta_free_allowances
        #if self.free_allowances_supply < 0:
        #    self.free_allowances_supply = 0

        #self.delta_sale_allowances = self.__sim_delta_sale_allowances_supply()
        #self.sale_allowances_supply = self.sale_allowances_supply + self.delta_sale_allowances
        #if self.sale_allowances_supply < 0:
        #    self.sale_allowances_supply = 0

        #self.delta_carbon_credits_supply = self.__sim_delta_carbon_credits_supply()
        #self.carbon_credit_supply      = self.carbon_credit_supply + self.delta_carbon_credits_supply
        #if self.carbon_credit_supply < 0:
        #    self.carbon_credit_supply = 0

        #self.delta_co2_subvention = self.__sim_delta_co2_subvention()
        #self.co2_subvention +=self.delta_co2_subvention
        #if self.co2_subvention < 0:
        #    self.co2_subvention = 0


        #self.delta_capital_nature =  self.__sim_delta_capital_nature()
        #self.capital_nature_sum +=  self.delta_capital_nature


    #def sim_co2_subvention(self, co2_subvention_last_year):
    #    co2_subvention = co2_subvention_last_year
    #    return co2_subvention


    #def __sim_delta_co2_subvention(self):
    #    delta_co2_subvention = random.choice(self.__delta_co2_subvention_pi)
    #    self.__delta_co2_subvention_pi.append(delta_co2_subvention)
    #    return delta_co2_subvention

    def __sim_delta_co2_consumption(self):
        sigma = stdev(self.__delta_co2_consumption_pi)#*0.02
        mu = mean(self.__delta_co2_consumption_pi)
        delta_co2_consumption = random.gauss(mu, sigma)#random.uniform(mu, mu-sigma)
        self.__delta_co2_consumption_pi.append(delta_co2_consumption)
        #print("delta_co2_consumption simulated", delta_co2_consumption)
        return delta_co2_consumption

    #def __sim_delta_free_allowances_supply(self):
    #    sigma = stdev(self.__delta_free_allowances_pi)
    #    mu = mean(self.__delta_free_allowances_pi)
    #    delta_free_allowances = random.gauss(mu, sigma)#random.uniform(mu, mu-sigma)
    #    self.__delta_free_allowances_pi.append(delta_free_allowances)
    #    return delta_free_allowances

    #def __sim_delta_sale_allowances_supply(self):
    #    sigma = stdev(self.__delta_sale_allowances_pi)
    #    mu = mean(self.__delta_sale_allowances_pi)
    #    delta_sale_allowances = random.gauss(mu, sigma)
    #    self.__delta_sale_allowances_pi.append(delta_sale_allowances)
    #    return delta_sale_allowances
    #def __sim_delta_carbon_credits_supply(self):
    #    sigma = stdev(self.__delta_carbon_credits_pi)
    #    mu = mean(self.__delta_carbon_credits_pi)
    #    delta_carbon_credits = random.gauss(mu, sigma)
    #    self.__delta_carbon_credits_pi.append(delta_carbon_credits)
    #    return delta_carbon_credits

    def __sim_start_co2_intensity(self):
        co2_intensity = 0
        while co2_intensity <= 0:
            mu = self.co2_intensity
            sigma = self.__assume['stdev_start_co2_intensity']
            co2_intensity = random.gauss(mu,sigma)
        return co2_intensity

    def sim_start_of_company(self, company_list, rest_of_the_world, co2_emission_total_start, co2_emission_sum_start):
        rest_of_the_world.co2_emission = co2_emission_total_start - co2_emission_sum_start
        rest_of_the_world.co2_intensity = rest_of_the_world.co2_emission/rest_of_the_world.business_value
        calc_emission_sum = 0
        random_values = np.random.rand(len(company_list))  # Erzeugt X zufällige Werte zwischen 0 und 1
        random_proportions = random_values / random_values.sum()  # Normalisieren auf Summe 1
        for index in company_list:
            company = company_list[index]
            company.co2_emission = co2_emission_sum_start * random_proportions[index]
            company.co2_intensity = company.co2_emission/company.business_value
            #self.__sim_start_co2_intensity()

            calc_emission_sum += company.co2_emission
        rest_emissions = co2_emission_sum_start - calc_emission_sum
        if rest_emissions != 0:
            id = random.randint(0, (len(company_list)-1))
            company = company_list[id]
            #company.co2_emission+= rest_emissions
        return
    def sim_entrance_new_company(self, company,
                                       cnt_company,
                                       rest_of_the_world):
        random_values = np.random.rand(cnt_company+1)
        random_proportions = random_values / random_values.sum()
        company.co2_emission = self.co2_emission_sum * random_proportions[-1] #last entrance shall be the new share of new entered company

        company.co2_intensity = self.__sim_start_co2_intensity()

        self.co2_emission_sum += company.co2_emission
        rest_of_the_world.co2_emission -= company.co2_emission

        return
    #def calc_company_start_situation(self, delta_business_value, emission_avg, stdev_emission):

    #    sigma = stdev_emission
    #    mu = emission_avg
    #    co2_emission = 0
    #    while co2_emission <= 0:
    #        co2_emission = random.gauss(mu, sigma)

        ### Fexibilisieren
    #    co2_intensity = self.co2_intensity

    #    delta_co2_emission = co2_intensity * delta_business_value

    #    share_of_subvention = random.uniform(0,0.2)
        #co2_subvention = self.co2_subvention * share_of_subvention

    #    return co2_emission, co2_intensity, co2_subvention

    def calc_company_nature_saldo(self, company):
        costs =[]
        incomes = []
        for option, list in self.invoice.items():
            for entry in list:
                if entry[0] == company:
                    costs.append(entry[2])
                if entry[1] == company:
                    incomes.append(entry[2])

        saldo = sum(incomes) - sum(costs)
        return saldo

    def sim_company_delta_co2_intensity(self, budget_to_improve_co2_intensity):
        #print("budget_to_improve_co2_intensity", budget_to_improve_co2_intensity)
        delta_co2_intensity = None
        if budget_to_improve_co2_intensity > 0:
            #-0.1 #TODO wieviel je nach budget
            #TODO abhängig von eigener historie nach 3 jahren
            sigma = stdev(self.__delta_co2_intensity_pi)#*0.02
            mu = mean(self.__delta_co2_intensity_pi)
            delta_co2_intensity = random.gauss(mu, sigma)

            #if co2_intensity < (delta_co2_intensity * -1):
            #    co2_intensity = co2_intensity + delta_co2_intensity
        return delta_co2_intensity
    def sim_company_co2_intensity(self, co2_intensity_ly):
        #print("co2-intensity: ",self.co2_intensity)
        mu = mean(self.__delta_co2_intensity_pi)
        #print("__delta_co2_intensity_mu: ",mu)
        sigma = stdev(self.__delta_co2_intensity_pi)
        influence_co2_intensity = random.gauss(mu, sigma)
        #if influence_co2_intensity > 0:
        #    influence_co2_intensity = delta_co2_intensity * -1
        #print("delta_co2_intensity: ",delta_co2_intensity)
        co2_intensity = co2_intensity_ly + influence_co2_intensity
        #delta_co2_intensity = 0
        return co2_intensity

    def calc_company_technical_improvement(self,budget_to_improve_co2_intensity,
                                           delta_business_value,
                                           business_value,
                                     co2_emission_last_year,
                                     co2_intensity,
                                     ):

        delta_co2_emission = (co2_intensity * delta_business_value)
        co2_emission = co2_emission_last_year + delta_co2_emission

        return co2_emission

        #print("co2_intensity", co2_intensity)
        #print("delta_business_value", delta_business_value)
        #print("delta_co2_emission", delta_co2_emission)



        #co2_emission = co2_intensity * business_value
        #print("co2_emission", co2_emission)
        #if co2_intensity < 0 or co2_emission < 0 or business_value < 0:
        #    return co2_emission_last_year

    def calc_company_marketing_improvement(self, budget_to_pay_off_emissions, co2_emission, is_co2_taxable):
        delta_marketing_influence = 0
        co2_cost = self.price_co2 * co2_emission
        overshoot = 0
        if not is_co2_taxable:
            #budget to pay off / price
            if co2_cost > budget_to_pay_off_emissions:
                delta_marketing_influence = +1 #TODO simulieren
                pass
            else:
                delta_marketing_influence = +3 #TODO simulieren
                pass
        else:
            overshoot =  budget_to_pay_off_emissions - co2_cost

        return delta_marketing_influence, overshoot

    #def calc_company_co2_emission(self, business_value, co2_intensity):
    #    co2_emission = co2_intensity * business_value
    #    return co2_emission




        #capital_nature_last_year,
        #co2_consumption_last_year,
        #co2_correlation_factor,
        #co2_subvention_last_year,
        #company,
        #market_influence_nature,
        #nature_power

        #co2_emission =  co2_emission_idle * math.exp((business_value) * co2_correlation_factor)
        #print("co2_emission: {0}".format(co2_emission))
        #print("co2_emission: {0}".format(co2_emission))
        #if self.co2_subvention == 0:
        #    self.co2_subvention = 0.00001
        #delta_co2_subvention_share = self.delta_co2_subvention / self.co2_subvention
        #co2_subvention = co2_subvention_last_year * (1 + delta_co2_subvention_share)

        #capital_nature, co2_consumption = self.__calc_company_co2_consumption(capital_nature_last_year,
        #                                              co2_consumption_last_year,
        #                                              market_influence_nature,
        #                                              nature_power)
        #capital_nature += co2_subvention
        #co2_supply = 0
        #co2_apply_free = 0
        #if co2_consumption > co2_emission:
        #    co2_supply = co2_consumption - co2_emission
        #else:
        #    co2_apply_free = co2_emission



        #capital_nature, co2_apply_free, co2_consumption, co2_emission, co2_supply

    #def calc_cross_sectoral_correction_factor(self):
    #    co2_free_apply = self.apply_free_sum
    #    if co2_free_apply <= 0:
    #        self.__cross_sectoral_correction_factor = 1
    #    else:
    #        self.__cross_sectoral_correction_factor = self.free_allowances_supply / co2_free_apply#

    #    if self.__cross_sectoral_correction_factor > 1 :
    #        self.__cross_sectoral_correction_factor = 1

    #    return self.__cross_sectoral_correction_factor

    def calc_supplier_price_by_demander_amount(self, demander_amount):
        low_limit = self.__assume['prices_lower_limit']

        min_price = self.__calc_min_price_production()
        factor = (self.capital_nature_sum/self.co2_emission_sum - min_price)/self.co2_emission_sum
        price = factor * demander_amount + min_price
        if price < low_limit: # lower than 80cent per tCo2
            price = low_limit
        return price
    def calc_demander_price_by_supplier_amount(self, supplier_amount):
        low_limit = self.__assume['prices_lower_limit']

        max_price = self.__calc_max_price_by_requirements()
        factor = max_price / self.co2_emission_sum
        price = factor * supplier_amount + max_price

        if price < low_limit: # lower than 80cent per tCo2
            price = low_limit
        return price
    def company_option_improve_nature_power(self, budget, nature_power_last_year):
        ##SET nature power
        limit = budget/nature_power_last_year
        delta_nature_power = random.uniform(0, limit)
        nature_power = nature_power_last_year + delta_nature_power
        return nature_power

    def company_option_improve_co2_intensity(self,budget, co2_intensity_last_year):
        ## SET co2_intensity
        limit = budget/co2_intensity_last_year
        delta_co2_intensity = random.uniform(0, limit)
        co2_intensity = co2_intensity_last_year + delta_co2_intensity
        return co2_intensity

    def company_option_apply_free_allowances(self, budget, company):
        company.is_applying = False
        if company.co2_apply_free > 0 and budget > 0:
            company.is_applying = True
            company.business_power -= 0.1
        return
    def company_interaction_buy_allowances(self,budget, company):
        return
    def __calc_company_co2_consumption(self, capital_nature_last_year,
                                       co2_consumption_last_year,
                                        market_influence_nature,
                                        nature_power
                                       ):

        capital_nature = capital_nature_last_year + co2_consumption_last_year * nature_power
        nature_value = co2_consumption_last_year + capital_nature * market_influence_nature
        co2_consumption = nature_value
        return capital_nature, co2_consumption

    def __calc_max_price_by_requirements(self):
        external_influence = 1.23
        price = self.capital_nature_sum / self.co2_emission_sum + external_influence
        return price

    def __calc_min_price_production(self):


        tendence = mean(self.__delta_co2_price_pi)
        forcast = 30 + tendence
        delta_demand_predicted = 500 #additional co2_emissions
        delta_capital_nature = 1000
        delta_production_costs = 0
        price = forcast - delta_production_costs + delta_capital_nature/(self.co2_emission_sum+delta_demand_predicted)


        return price
    def __get_min_price_government(self, year):
        #Brennstoffemissionshandelsgesetz: nationaler Emissionshandel Deutschland
        dict_prices = {2021:25,
                       2022:30,
                       2023:35,
                       2024:40,
                       2025:50,
                       2026:(55,65)}

        if year in dict_prices:
            return dict_prices[year]
        return 0 # per_tone
    def get_tax_price_per_mio_metric_ton(self, year):
        return self.__get_min_price_government(year) * 1000000


















    def optimize_markt_price_competitive(self,company_list, try_price):
        optimum_price = 30
        try_price = abs(try_price)

        maximum_winning = -1
        price_winning_dict = {}
        cnt_trails = 0
        while cnt_trails < 100 :
            current_winning = 0
            for index in company_list:
                company = company_list[index]
                current_winning += 0.0#company.calc_co2_demand(try_price) * try_price
            price_winning_dict[try_price] = current_winning

            if maximum_winning < current_winning:
                maximum_winning = current_winning
                try_price += 0.1
            else:
                try_price -= 0.01
                cnt_trails += 1
        # sort dict by value
        sorted_data = sorted(price_winning_dict.items(), key=lambda x: x[1], reverse=True)

        # price with maximum winning value
        optimum_price = sorted_data[0][0]
        #print("price_winning_dict: {0}".format(sorted_data))
        #print("optimum_price: {0}".format(optimum_price))

        return optimum_price

    #def sell_co2_consumption(self, supplier, demander):
    #    demand = demander.calc_co2_demand(self.)
    #    supply = supplier.get_available_supply()
    #    amount = min (supply, demand)
    #    demander.buy(amount, self.)
    #    supplier.sell(amount, self.)
    #    return

    def optimize_markt_price_valuebased(self,company_list, try_price):
        ##to do: Impact price optimierung, stimmt das so???
        print("TODO: Verify optimization algorithm for value based prize optimization")
        optimum_price = abs(self.get_impact_price())
        try_price = abs(try_price)

        maximum_winning = -1
        price_winning_dict = {}
        cnt_trails = 0
        while cnt_trails < 100 :
            current_winning = 0
            for index in company_list:
                company = company_list[index]
                current_winning += 0.0#company.calc_impact_demand(try_price) * try_price
            price_winning_dict[try_price] = current_winning

            if maximum_winning < current_winning:
                maximum_winning = current_winning
                try_price += 0.1
            else:
                try_price -= 0.01
                cnt_trails += 1
        # sort dict by value
        sorted_data = sorted(price_winning_dict.items(), key=lambda x: x[1], reverse=True)

        # price with maximum winning value
        optimum_price = sorted_data[0][0]
        print("price_winning_dict: {0}".format(sorted_data))
        print("optimum_price: {0}".format(optimum_price))

        return optimum_price

    def price_finding_to_sale_allowances(self, company_list):
        supplier_prices = [self.price_allowances]
        demander = [company_list[index] for index in company_list if company_list[index].co2_demand > 0]
        for company in demander:
            demander_amount = company.co2_demand
            supplier_prices.append(self.calc_supplier_price_by_demander_amount(demander_amount))

        demander_price = self.calc_demander_price_by_supplier_amount(self.sale_allowances_supply)


        #### ASSUMPTION!!!!
        self.price_allowances = random.gauss(mean([demander_price, mean(supplier_prices)]), stdev([demander_price, mean(supplier_prices)]))
        return demander
    def get_impact_price(self):
        return self.__calc_impact_price(self.price_allowances, self.state_of_atmosphere)

    def __calc_new_state_of_atmosphere(self,state_of_atmosphere, co2_consumption_ly, total_emission_ly):

        r_convert = self.__assume['r_convert']

        add_on = (total_emission_ly - co2_consumption_ly)/ r_convert
        new_state = state_of_atmosphere + add_on
        return new_state

    def __calc_impact_price(self, co2_price, state_of_atmosphere, co2_em = 1, optimum=280, threshold=350):
        r_convert = self.__assume['r_convert']
        v_ppm = co2_em / r_convert ## change of atmospheric state by human impact in ppm
        #c_co2 = co2_consum / r_factor

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
        f_of_change = self.a * (state_of_atmosphere+v_ppm)**2 + self.b * (state_of_atmosphere + v_ppm) + self.c
        impact = f_of_change-f_of_state
        impact_per_tco2 = impact / co2_em
        impact_price = co2_price /  impact_per_tco2
        return impact_price

    def log_to_journal(self, logId):
        self.journal[logId] = {}
        self.journal[logId]['state_of_atmosphere']      = float(self.state_of_atmosphere)
        self.journal[logId]['capital_nature_sum']       = float(self.capital_nature_sum)
        self.journal[logId]['co2_consumption']          = float(self.co2_consumption)
        self.journal[logId]['co2_emission_sum']         = float(self.co2_emission_sum)
        self.journal[logId]['co2_intensity']            = float(self.co2_intensity)
        #self.journal[logId]['co2_subvention']           = float(self.co2_subvention)
        #self.journal[logId]['free_allowances_supply']   = float(self.free_allowances_supply)
        #self.journal[logId]['granted_free_sum']         = float(self.granted_free_sum)
        #self.journal[logId]['invoice'] =                        self.invoice
        #self.journal[logId]['sale_allowances_supply']   = float(self.sale_allowances_supply)
        #self.journal[logId]['sold_allowances_sum']      = float(self.sold_allowances_sum)
        #self.journal[logId]['remaining_stock_sum']      = float(self.remaining_stock_sum)

        self.invoice ={
            #           (Demander, Supplier, Sales price, tCo2)
                    'free' : [(None,None,0.0,0.0)],
                    'sale' : [(None,None,0.0,0.0)],
                    'vcm'  : [(None,None,0.0,0.0)],
                    'tax'  : [(None,None,0.0,0.0)]
                    }
        return self.journal
    def to_dict(self):
        return {
            'state_of_atmosphere' :        float(self.state_of_atmosphere),
            'capital_nature_sum':          float(self.capital_nature_sum),
            'co2_consumption'     :        float(self.co2_consumption),
            'co2_emission_sum':            float(self.co2_emission_sum),
            'co2_intensity':               float(self.co2_intensity),
            #'co2_subvention':              float(self.co2_subvention),
            #'free_allowances_supply':      float(self.free_allowances_supply),
            #'granted_free_sum':            float(self.granted_free_sum),
            #'invoice':                           self.invoice,
            #'sale_allowances_supply':      float(self.sale_allowances_supply),
            #'sold_allowances_sum':         float(self.sold_allowances_sum),
            #'remaining_stock_sum':         float(self.remaining_stock_sum),
        }
