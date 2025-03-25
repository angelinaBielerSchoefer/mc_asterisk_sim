import random

#from scipy.special import delta

from Company import Company
from statistics import stdev, mean


class Playground:
    def __init__(self, assume,
                 business_power_pi,
         #        start_business_value_share,
         #        start_business_capital,
         #        start_total_capital,
         #        start_capital_share,
         #        delta_co2_emission_global_pi,
         #        delta_gdp_pi,
         #        start_co2_emission_global,
         #        start_delta_gdp,
         #        co2_investment_share_pi,
         #        start_gdp,
                 market_condition_pi):
        self.__assume = assume
        self.__business_power_pi = business_power_pi
        #self.__co2_investment_share_pi =co2_investment_share_pi
        self.__market_condition_pi = market_condition_pi
        #self.__delta_co2_emission_global_pi = delta_co2_emission_global_pi
        #self.__delta_gdp_pi = delta_gdp_pi
        #self.__set_business_power_global()
        #self.__set_market_condition_global()

        #self.start_business_value_share = start_business_value_share
        #self.start_capital_share = start_capital_share

        #self.co2_emission_global = start_co2_emission_global
        #self.count_company = 0
        #self.gdp = start_gdp
        #self.start_delta_gdp = start_delta_gdp
        #self.rest_of_the_world = None
        #self.capital_total = start_total_capital
        #self.capital_business = start_business_capital

    def sim_start_of_company(self, num_actors):
        #### Start values provided by data
        ### normal distributed

        mu = random.uniform(0,1000)#self.gdp * self.start_business_value_share / num_actors
        sigma = random.random() #self.__assume['stdev_start_value'] / num_actors
        business_value = random.gauss(mu, sigma)

        #mu = self.start_delta_gdp * self.start_business_value_share / num_actors
        #sigma = stdev(self.__delta_gdp_pi) * self.start_business_value_share / num_actors
        delta_business_value = random.gauss(mu, sigma)

        #mu = self.capital_business * self.start_capital_share / num_actors
        #sigma = self.__assume['stdev_start_assets']
        business_capital = random.gauss(mu, sigma)

        #mu = mean(self.__co2_investment_share_pi)
        #sigma = stdev(self.__co2_investment_share_pi)

        #weight_nature = random.gauss(mu, sigma)
        #capital_nature = weight_nature*capital

        return  business_capital, business_value, delta_business_value