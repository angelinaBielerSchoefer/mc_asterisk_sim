import random
from statistics import mean, stdev

from mesonbuild.scripts.env2mfile import detect_missing_native_binaries


class MarketCo2:
    def __init__(self, assume,
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
                 delta_free_allowance_pi,
                 delta_sale_allowance_pi,
                 free_allowances_start,
                 sale_allowances_start,
                 ):
        self.__assume = assume
        self.__cross_sectoral_correction_factor = free_allowances_start / co2_emission_big_start
        self.__delta_co2_emission_pi        = delta_co2_emission_pi
        self.__delta_co2_intensity_pi       = delta_co2_intensity_pi
        self.__delta_co2_price_pi           = delta_co2_price_pi
        self.__delta_co2_subvention_pi      = delta_co2_subvention_pi
        self.__delta_capital_nature_pi      = delta_capital_nature_pi
        self.__delta_free_allowances_pi     = delta_free_allowance_pi
        self.__delta_sale_allowances_pi     = delta_sale_allowance_pi
        self.__factor_free_allowances       = 1 - assume['reduce_free_allowances']

        self.free_allowances    = free_allowances_start
        self.sale_allowances    = sale_allowances_start
        self.co2_emission_big   = co2_emission_big_start

        self.co2_intensity      = co2_intensity_start
        self.co2_price          = co2_price_start
        self.co2_subvention     = co2_subvention_start
        self.co2_supply         = co2_supply_start
        self.delta_co2_intensity = self.__sim_delta_co2_intensity()
        self.delta_co2_subvention = self.__sim_delta_co2_subvention()
        self.delta_free_allowances = self.__sim_delta_free_allowances()
        self.delta_sale_allowances = self.__sim_co2_delta_sale_allowances()

        self.state_of_atmosphere = 0
        total_capital_nature_start = 10000
        self.delta_capital_nature = 0
        self.total_capital_nature = total_capital_nature_start
        self.invoice = {
            #           Demander, Supplier, Sales price, tCo2
            'free' : [(None,None,0.0,0.0)],
            'sale' : [(None,None,0.0,0.0)],
            'vcm'  : [(None,None,0.0,0.0)],
            'tax'  : [(None,None,0.0,0.0)]
        }

        self.journal={
            -1: {
                'state_of_atmosphere': float(self.state_of_atmosphere),
                'total_capital_nature': float(self.total_capital_nature),
                'co2_emission_big': float(self.co2_emission_big),
                'co2_intensity': float(self.co2_intensity),
                'co2_price': float(self.co2_price),
                'co2_subvention':float(self.co2_subvention),
                'co2_supply': float(self.co2_supply),
                'free_allowances': float(self.free_allowances),
                'invoice': self.invoice,
                'sale_allowances': float(self.sale_allowances),
            }
        }



        self.co2_balance = 0
        return

    def sim_new_year_co2(self):#, delta_co2_intensity_last_year):
        # sim co2 intesity delta

        self.delta_co2_intensity = self.__sim_delta_co2_intensity()
        self.co2_intensity += self.delta_co2_intensity

        self.co2_supply = 30000

        self.delta_free_allowances = self.__sim_delta_free_allowances()
        self.free_allowances = self.free_allowances + self.delta_free_allowances
        if self.free_allowances < 0:
            self.free_allowances = 0
        #
        self.delta_sale_allowances = self.__sim_co2_delta_sale_allowances()
        self.sale_allowances = self.sale_allowances + self.delta_sale_allowances
        if self.sale_allowances < 0:
            self.sale_allowances = 0

        self.delta_co2_subvention = self.__sim_delta_co2_subvention()
        self.co2_subvention +=self.delta_co2_subvention
        if self.co2_subvention < 0:
            self.co2_subvention = 0


        self.delta_capital_nature =  self.__sim_delta_capital_nature()
        self.total_capital_nature +=  self.delta_capital_nature

        return self.total_capital_nature

    def sim_co2_intensity(self, co2_intensity_last_year):
        mu = self.delta_co2_intensity
        deviation = self.__assume['stdev_delta_co2_intensity']
        delta_co2_intensity = random.uniform(mu+deviation,mu-deviation)
        co2_intensity = delta_co2_intensity+co2_intensity_last_year
        return co2_intensity
    def sim_co2_subvention(self, co2_subvention_last_year):
        co2_subvention = co2_subvention_last_year


        return co2_subvention
    def __sim_delta_capital_nature(self):
        sigma = stdev(self.__delta_capital_nature_pi)
        mu = mean(self.__delta_capital_nature_pi)
        delta_capital_nature = random.gauss(mu, sigma)
        return delta_capital_nature
    def __sim_delta_co2_subvention(self):
        delta_co2_subvention = random.choice(self.__delta_co2_subvention_pi)
        self.__delta_co2_subvention_pi.append(delta_co2_subvention)
        return delta_co2_subvention
    def __sim_delta_co2_intensity(self):
        delta_co2_intensity = random.gauss(mean(self.__delta_co2_intensity_pi),stdev(self.__delta_co2_intensity_pi))
        self.__delta_co2_intensity_pi.append(delta_co2_intensity)
        return delta_co2_intensity
    def __sim_delta_free_allowances(self):
        sigma = stdev(self.__delta_free_allowances_pi)
        mu = mean(self.__delta_free_allowances_pi)
        delta_free_allowances = random.uniform(mu, mu-sigma)
        self.__delta_free_allowances_pi.append(delta_free_allowances)
        return delta_free_allowances

    def __sim_co2_delta_sale_allowances(self):
        sigma = stdev(self.__delta_sale_allowances_pi)
        mu = mean(self.__delta_sale_allowances_pi)
        delta_sale_allowances = random.gauss(mu, sigma)
        self.__delta_sale_allowances_pi.append(delta_sale_allowances)
        return delta_sale_allowances

    def calc_company_start_situation(self, business_value, share_of_co2_idle):
        sigma = self.__assume['stdev_start_co2_intensity']
        mu = self.co2_intensity
        co2_intensity = random.gauss(mu, sigma)
        co2_emission = co2_intensity*business_value
        co2_emission_idle = co2_emission*share_of_co2_idle
        co2_intensity = (co2_emission-co2_emission_idle)/business_value
        share_of_subvention = 0.2
        co2_subvention = self.co2_subvention * share_of_subvention
        return co2_emission, co2_intensity, co2_emission_idle, co2_subvention

    def calc_co2_market_situation_company(self, business_value,
                                          capital,
                                          co2_emission_idle,
                                          co2_intensity_last_year,
                                          co2_subvention_last_year,
                                          weight_nature):
        ##ASSUMPTION, calculation required
        co2_intensity = self.sim_co2_intensity(co2_intensity_last_year)
        co2_emission = co2_intensity * business_value + co2_emission_idle
        if self.co2_subvention == 0:
            self.co2_subvention = 0.00001
        delta_co2_subvention_share = self.delta_co2_subvention / self.co2_subvention
        co2_subvention = co2_subvention_last_year * (1 + delta_co2_subvention_share)
        capital_nature = capital * weight_nature + co2_subvention



        co2_apply_free = co2_emission
        return co2_intensity, capital_nature, co2_apply_free, co2_emission

    def calc_cross_sectoral_correction_factor(self, co2_free_apply):
        if co2_free_apply == 0:
            self.__cross_sectoral_correction_factor = 1
        else:
            self.__cross_sectoral_correction_factor = self.free_allowances / co2_free_apply

        if self.__cross_sectoral_correction_factor > 1 :
            self.__cross_sectoral_correction_factor = 1

        return self.__cross_sectoral_correction_factor
    def calc_supplier_price_by_demander_amount(self, demander_amount):
        low_limit = self.__assume['prices_lower_limit']

        min_price = self.__calc_min_price_production()
        factor = (self.total_capital_nature/self.co2_emission_big - min_price)/self.co2_emission_big
        price = factor * demander_amount + min_price
        if price < low_limit: # lower than 80cent per tCo2
            price = low_limit
        return price

    def calc_demander_price_by_supplier_amount(self, supplier_amount):
        low_limit = self.__assume['prices_lower_limit']

        max_price = self.__calc_max_price_by_requirements()
        factor = max_price / self.co2_emission_big
        price = factor * supplier_amount + max_price

        if price < low_limit: # lower than 80cent per tCo2
            price = low_limit
        return price

    def __calc_max_price_by_requirements(self):
        external_influence = 1.23
        price = self.total_capital_nature / self.co2_emission_big + external_influence
        return price

    def __calc_min_price_production(self):
        tendence = mean(self.__delta_co2_price_pi)
        forcast = self.co2_price + tendence
        delta_demand_predicted = 500 #additional co2_emissions
        delta_capital_nature = 1000
        delta_production_costs = 0
        price = forcast - delta_production_costs + delta_capital_nature/(self.co2_emission_big+delta_demand_predicted)
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


















    def optimize_markt_price_competitive(self,company_list, try_price):
        optimum_price = abs(self.co2_price)
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
        #print("self.co2_price: {0}".format(self.co2_price))

        return optimum_price

    #def sell_co2_consumption(self, supplier, demander):
    #    demand = demander.calc_co2_demand(self.co2_price)
    #    supply = supplier.get_available_supply()
    #    amount = min (supply, demand)
    #    demander.buy(amount, self.co2_price)
    #    supplier.sell(amount, self.co2_price)
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
        print("self.co2_price: {0}".format(self.co2_price))

        return optimum_price
    def __calc_impact_price_pi(self):
        impact_price = []
        #for co2_price in self.__co2_price_pi:
        #    new_price = self.__calc_impact_price(co2_price, self.state_of_atmosphere)
        #    impact_price.append(new_price)
        return impact_price

    def price_finding_to_sale_allowances(self, company_list):
        supplier_prices = [self.co2_price]
        demander = [company_list[index] for index in company_list if company_list[index].co2_demand > 0]
        for company in demander:
            demander_amount = company.co2_demand
            supplier_prices.append(self.calc_supplier_price_by_demander_amount(demander_amount))

        demander_price = self.calc_demander_price_by_supplier_amount(self.co2_supply)
        #### ASSUMPTION!!!!!
        self.co2_price = random.gauss(mean([demander_price, mean(supplier_prices)]), stdev([demander_price, mean(supplier_prices)]))
        return demander
    def get_impact_price(self):
        return self.__calc_impact_price(self.co2_price, self.state_of_atmosphere)

    def __calc_impact_price(self, co2_price, state_of_atmosphere, co2_em = 1, optimum=280, threshold=350):

        #https://wiki.bildungsserver.de/klimawandel/index.php/Kohlendioxid-Konzentration
        #  1 ppm CO2 = 7,814 Gt CO2
        # co2_em and co2_consumption given in Gt CO2
        r_factor = 7.814

        v_co2 = co2_em / r_factor ## change of atmospheric state by human impact in ppm
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
        f_of_change = self.a * (state_of_atmosphere+v_co2)**2 + self.b * (state_of_atmosphere + v_co2) + self.c
        impact = f_of_change-f_of_state
        impact_per_gtco2 = impact / co2_em
        impact_price = co2_price /  impact_per_gtco2
        return impact_price

    def log_to_journal(self, logId):
        self.journal[logId] = {}
        self.journal[logId]['state_of_atmosphere'] = float(self.state_of_atmosphere)
        self.journal[logId]['total_capital_nature'] = float(self.total_capital_nature)
        self.journal[logId]['co2_emission_big'] = float(self.co2_emission_big)
        self.journal[logId]['co2_intensity'] = float(self.co2_intensity)
        self.journal[logId]['co2_price'] = float(self.co2_price)
        self.journal[logId]['co2_subvention'] = float(self.co2_subvention)
        self.journal[logId]['co2_supply'] = float(self.co2_supply)
        self.journal[logId]['free_allowances'] = float(self.free_allowances)
        self.journal[logId]['invoice'] = self.invoice
        self.journal[logId]['sale_allowances'] = float(self.sale_allowances)

        return self.journal
    def to_dict(self):
        return {
            'state_of_atmosphere': float(self.state_of_atmosphere),
            'total_capital_nature': float(self.total_capital_nature),
            'co2_emission_big': float(self.co2_emission_big),
            'co2_intensity' : float(self.co2_intensity),
            'co2_price': float(self.co2_price),
            'co2_supply': float(self.co2_supply),
            'co2_subvention':float(self.co2_subvention),
            'free_allowances': float(self.free_allowances),
            'invoice': self.invoice,
            'sale_allowances': float(self.sale_allowances),
        }
