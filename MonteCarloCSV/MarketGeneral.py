import random

#from Cython.Shadow import returns

#from scipy.special import delta

from Company import Company
from statistics import stdev, mean


class MarketGeneral:
    def __init__(self, assume,
                 business_power_pi,
                 start_business_value_share,
                 start_capital_business,
                 start_capital_total,
                 start_capital_share,
                 delta_co2_emission_global_pi,
                 delta_gdp_pi,
                 delta_market_condition_pi,
                 start_co2_emission_global,
                 start_delta_gdp,
                 co2_investment_share_pi,
                 start_gdp,
                 market_condition_pi
                 ):
        self.__assume = assume
        self.__business_power_pi = business_power_pi
        self.__co2_investment_share_pi =co2_investment_share_pi
        self.__share_invest_marketing_pi = co2_investment_share_pi #TODO: daten prüfem
        self.__share_invest_technology_pi = co2_investment_share_pi #TODO daten prüfem
        self.__market_condition_pi = market_condition_pi
        self.__delta_market_condition_pi = delta_market_condition_pi
        self.__delta_co2_emission_global_pi = delta_co2_emission_global_pi
        self.__delta_gdp_pi = delta_gdp_pi

        self.__set_business_power_global()
        self.market_condition = 0
        self.__set_market_condition_global()

        self.start_business_value_share = start_business_value_share
        self.start_capital_share = start_capital_share

        self.co2_emission_global = start_co2_emission_global
        self.count_company = 0
        self.gdp = start_gdp
        self.start_delta_gdp = start_delta_gdp
        self.rest_of_the_world = None
        self.capital_total = start_capital_total
        self.capital_business = start_capital_business
        self.business_value_sum = self.gdp * self.start_business_value_share


        self.journal={
            -1: {
                'business_power'    : float(self.business_power),
                'business_value_sum'    : float(self.business_value_sum),
                'capital_total'     : float(self.capital_total),
                'capital_business'  : float(self.capital_business),
                'co2_emission_global': float(self.co2_emission_global),
                'count_company'     : int(self.count_company),
                'gdp'               : float(self.gdp),
                'market_condition'  : float(self.market_condition),
            }
        }
    def __set_business_power_global(self):
        self.business_power =  random.gauss(mean(self.__business_power_pi),stdev(self.__business_power_pi))#random.choice(self.__business_power_pi) #self.__global_bp_history[year]
        self.__business_power_pi.append(self.business_power)
        return

    def __set_market_condition_global(self):
        new_market_condition = random.gauss(mean(self.__market_condition_pi),stdev(self.__market_condition_pi))#random.choice(self.__market_condition_pi)#self.__global_mc_history[year]
        self.delta_market_condition = self.market_condition - new_market_condition
        self.market_condition = new_market_condition
        self.__market_condition_pi.append(self.market_condition)
        return

    def __set_emission_global(self):
        delta_co2_emission_global = random.gauss(mean(self.__delta_co2_emission_global_pi),stdev(self.__delta_co2_emission_global_pi))#random.choice(self.__market_condition_pi)#self.__global_mc_history[year]
        self.__delta_co2_emission_global_pi.append(delta_co2_emission_global)
        self.co2_emission_global +=delta_co2_emission_global
        return

    def sim_new_year(self):
        self.__set_business_power_global()
        self.__set_market_condition_global()
        #self.__set_emission_global()
        return self

    def sim_start_of_company(self, num_companies, entrance_year):
        #### Start values provided by data
        ### normal distributed

        mu = self.gdp * self.start_business_value_share / num_companies
        sigma = self.__assume['stdev_start_value'] / num_companies
        business_value = random.gauss(mu, sigma)

        mu = self.start_delta_gdp * self.start_business_value_share / num_companies
        sigma = stdev(self.__delta_gdp_pi) * self.start_business_value_share / num_companies
        delta_business_value = random.gauss(mu, sigma)

        mu = self.capital_business * self.start_capital_share / num_companies
        sigma = self.__assume['stdev_start_assets']
        capital = random.gauss(mu, sigma)

        mu = mean(self.__co2_investment_share_pi)
        sigma = stdev(self.__co2_investment_share_pi)

        weight_nature = random.gauss(mu, sigma)
        capital_nature = weight_nature*capital
        journal = {}

        business_value_r = business_value
        capital_r = capital
        year = entrance_year - 1
        while year > (entrance_year - 10):

            if not year in journal:
                journal[year] = {}
            business_value_r, capital_r = self.__sim_reverse_journal(business_value_r, capital_r, num_companies)
            journal[year]['business_value'] = business_value_r
            journal[year]['capital']        = capital_r
            year -= 1

        return  business_value, capital, capital_nature, delta_business_value, journal

    def sim_start_rest_of_the_world(self, company_list):
        sum_bv = sum([company_list[index].business_value for index in company_list])
        bv_row = self.gdp - sum_bv
        sum_cap = sum([company_list[index].capital for index in company_list])
        cap_row = self.capital_business - sum_cap
        investment_of_nature = 0 ##todo: calculate, set oder simulate??
        self.rest_of_the_world = Company(bv_row,cap_row,investment_of_nature)
        return self.rest_of_the_world

    def sim_company_situation(self, company):
        ### simulated factors bp, mi
        ### random distributed with assumed deviation
        mu = self.business_power
        deviation = self.__assume['stdev_business_power']
        business_power = random.gauss(mu, deviation)
        #business_power = random.uniform(mu-deviation, mu+deviation)

        mu = self.market_condition
        deviation = self.__assume['stdev_market_influence']
        market_influence = random.gauss(mu,deviation)
        #market_influence = random.uniform(mu-deviation, mu+deviation)


        is_alive = self.check_company_if_survived(company)

        return business_power, is_alive, market_influence
    def sim_company_start_year(self, business_power, capital_ly, delta_capital_ly, delta_market_influence_ly, market_influence_ly):
        market_influence = (market_influence_ly +
                            delta_market_influence_ly +
                            self.delta_market_condition) #TODO randomize??
        capital = capital_ly + delta_capital_ly
        business_power = business_power #TODO: randomize
        return business_power, capital, market_influence


    #def sim_investment_share(self):
    #    mu = mean(self.__co2_investment_share_pi)
    #    sigma = stdev(self.__co2_investment_share_pi)
    #    investment_share = random.gauss(mu, sigma)
    #    return investment_share
    #def sim_market_influence(self, budget_limit_to_pay_off_emissions, market_influence):
    #    #to do: abhängig vom budget
    #    mu = market_influence
    #    sigma = self.__assume['stdev_market_influence']
    #    delta_market_influence = random.gauss(mu,sigma)
    #    return delta_market_influence

    def sim_share_mark_invest(self):
        #TO DO abhängigkeit zu company performance
        mu = mean(self.__share_invest_marketing_pi)
        sigma = stdev(self.__share_invest_marketing_pi)
        investment_share = random.gauss(mu, sigma)
        return investment_share
    def sim_share_tech_invest(self):
        #TO DO abhängigkeit zu company performance
        mu = mean(self.__share_invest_technology_pi)
        sigma = stdev(self.__share_invest_technology_pi)
        investment_share = random.gauss(mu, sigma)
        return investment_share
    def sim_company_delta_market_influence(self):
        #to do: abhängig vom budget
        mu = mean(self.__delta_market_condition_pi)
        sigma = stdev(self.__delta_market_condition_pi)
        delta_market_influence = random.gauss(mu,sigma)
        return delta_market_influence

    def __sim_reverse_journal(self, business_value, capital, num_companies):
        mu = self.start_delta_gdp * self.start_business_value_share / num_companies
        sigma = stdev(self.__delta_gdp_pi) * self.start_business_value_share /num_companies
        delta_business_value = random.gauss(mu, sigma)

        mu = self.start_delta_gdp * self.start_business_value_share / num_companies
        sigma = stdev(self.__delta_gdp_pi) * self.start_business_value_share /num_companies
        delta_capital = random.gauss(mu, sigma)

        business_value -= delta_business_value
        capital -= delta_capital
        return  business_value, capital

    def check_company_if_survived(self, company):
        year = max(company.journal.keys())
        death_counter = 0
        while year in company.journal:
            if company.journal[year]['business_value'] < 0 and company.journal[year]['capital'] < 0:
                death_counter += 1
                year -= 1
            else:
                year = 0

        limit = random.gauss(7.5, 2.5)
        if death_counter > limit:
            company.is_alive = False

        return company.is_alive

    def calc_co2_emission_row(self):
        co2_intensity = self.rest_of_the_world.co2_intensity
        delta_business_value = self.rest_of_the_world.delta_business_value
        co2_emission_last_year = self.rest_of_the_world.co2_emission
        delta_co2_emission = (co2_intensity * delta_business_value)
        co2_emission = co2_emission_last_year + delta_co2_emission

        self.rest_of_the_world.co2_emission = co2_emission
        return


    def calc_company_capital(self,
                             business_power_last_year,
                             business_value_last_year,
                             capital_last_year):
        delta_capital = (business_value_last_year * business_power_last_year)
        capital =  delta_capital + capital_last_year
        return capital, delta_capital

    def calc_company_business_value(self, business_value_last_year,
                                    capital_business,
                                    market_influence):

        delta_business_value = capital_business * market_influence
        business_value = business_value_last_year + delta_business_value

        return business_value, delta_business_value
    #def calc_company_situation
    def calc_row_situation(self):
        business_value_last_year = self.rest_of_the_world.business_value
        capital_last_year = self.rest_of_the_world.capital
        business_power_last_year = self.rest_of_the_world.business_power

        (self.rest_of_the_world.capital,
         self.rest_of_the_world.delta_capital) = self.calc_company_capital(business_power_last_year,
                                                                           business_value_last_year,
                                                                           capital_last_year)

        self.rest_of_the_world.capital_business = self.rest_of_the_world.capital
        self.rest_of_the_world.capital_nature = 0

        (self.rest_of_the_world.business_value,
         self.rest_of_the_world.delta_business_value) = self.calc_company_business_value(business_value_last_year,
                                                                                         self.rest_of_the_world.capital,
                                                                                         self.rest_of_the_world.market_influence)
        return

    def log_to_journal(self, logId):
        self.journal[logId] = {}
        self.journal[logId]['business_power'] = float(self.business_power)
        self.journal[logId]['business_value_sum'] = float(self.business_value_sum)
        self.journal[logId]['capital_business'] = float(self.capital_business)
        self.journal[logId]['capital_total'] = float(self.capital_total)
        self.journal[logId]['co2_emission_global'] = float(self.co2_emission_global)
        self.journal[logId]['count_company'] = int(self.count_company)
        self.journal[logId]['gdp'] = float(self.gdp)
        self.journal[logId]['market_condition'] = float(self.market_condition)
        return self.journal

    def to_dict(self):
        return {
            'business_power': float(self.business_power),
            'business_value_sum': float(self.business_value_sum),
            'capital_total': float(self.capital_total),
            'capital_business': float(self.capital_business),
            'co2_emission_global': float(self.co2_emission_global),
            'count_company': int(self.count_company),
            'gdp': float(self.gdp),
            'market_condition': float(self.market_condition),

        }