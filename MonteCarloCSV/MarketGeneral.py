import random
from Company import Company
from statistics import stdev, mean


class MarketGeneral:
    def __init__(self, assume,
                 business_power_pi,
                 start_business_value_share,
                 start_capital_share,
                 start_co2_emission_total,
                 co2_investment_share_pi,
                 gdp_start,
                 investment_by_category,
                 market_condition_pi,
                 start_year,
                 total_assets_start):
        self.__market_condition_pi = market_condition_pi
        self.__business_power_pi = business_power_pi
        self.__co2_investment_share_pi =co2_investment_share_pi
        self.__assume = assume
        self.rest_of_the_world = None

        self.__set_business_power_global()
        self.__set_market_condition_global()

        self.gdp = gdp_start
        self.count_company = 0
        self.co2_emission_total = start_co2_emission_total
        self.start_business_value_share = start_business_value_share
        self.start_capital_share = start_capital_share
        self.total_assets = total_assets_start

        investment = {}
        for category, data in investment_by_category.items():
            if start_year in data:
                investment[category] = data[start_year]
            else:
                print("no start value for sales volume category {0} found.".format(category))
        self.investment_by_category = investment

        self.journal={
            -1: {
                'business_power': float(self.business_power),
                'co2_emission_total': float(self.co2_emission_total),
                'count_company': int(self.count_company),
                'gdp': float(self.gdp),
                'market_condition': float(self.market_condition),
                'total_assets': float(self.total_assets),
            }
        }
    def __set_business_power_global(self):
        self.business_power =  random.gauss(mean(self.__business_power_pi),stdev(self.__business_power_pi))#random.choice(self.__business_power_pi) #self.__global_bp_history[year]
        self.__business_power_pi.append(self.business_power)
        return

    def __set_market_condition_global(self):
        self.market_condition = random.gauss(mean(self.__market_condition_pi),stdev(self.__market_condition_pi))#random.choice(self.__market_condition_pi)#self.__global_mc_history[year]
        self.__market_condition_pi.append(self.market_condition)
        return

    def sim_new_year(self):
        self.__set_business_power_global()
        self.__set_market_condition_global()
        return self

    def sim_start_of_company(self, num_companies):
        #### Start values provided by data
        ### normal distributed
        mu = self.gdp * self.start_business_value_share / num_companies
        sigma = self.__assume['stdev_start_value']/num_companies
        business_value = random.gauss(mu, sigma)
        mu = self.total_assets * self.start_capital_share / num_companies
        sigma = self.__assume['stdev_start_assets']
        capital = random.gauss(mu, sigma)
        capital_business = capital
        #category_of_capital = self.__get_sales_volume_category(capital)
        mu = mean(self.__co2_investment_share_pi) #self.investment_by_category[category_of_capital]

        #sigma = self.__assume['stdev_start_invest']
        sigma = stdev(self.__co2_investment_share_pi)

        weight_nature = random.gauss(mu, sigma)
        self.count_company = num_companies
        return  business_value, capital, weight_nature

    def sim_start_rest_of_the_world(self, company_list):
        sum_bv = sum([company_list[index].business_value for index in company_list])
        bv_row = self.gdp - sum_bv
        sum_cap = sum([company_list[index].capital for index in company_list])
        cap_row = self.total_assets - sum_cap
        investment_of_nature = 0 ##todo: calculate, set oder simulate??
        self.rest_of_the_world = Company(bv_row,cap_row,investment_of_nature)
        return self.rest_of_the_world

    def sim_general_market_situation_company(self, company):
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


        is_alive = self.__check_if_survived(company)

        return business_power, is_alive, market_influence
    def __check_if_survived(self, company):
        year = max(company.journal.keys())
        death_counter = 0
        while year in company.journal:
            if company.journal[year]['business_value'] < 0 and company.journal[year]['capital'] < 0:
                death_counter += 1
                year -= 1
            else:
                year = 0
        if death_counter > 10:
            company.is_alive = False

        return company.is_alive

    def calc_total_assets(self, company_list):

        total_assets = 0
        for index in company_list:
            company = company_list[index]

            if company.is_alive:
                total_assets += company.capital
        self.total_assets = total_assets + self.rest_of_the_world.capital
        return self.total_assets





    def calc_general_situation_company(self,
                                      business_power_last_year,
                                      business_value_last_year,
                                      capital_last_year,
                                      market_influence,
                                      weight_nature
                                      ):
        delta_capital = (business_value_last_year * business_power_last_year)
        capital =  delta_capital + capital_last_year

        weight_nature = 0
        weight_business = 1 - weight_nature
        capital_business = capital * weight_business
        capital_nature = capital * weight_nature


        delta_business_value = capital_business * market_influence
        business_value = business_value_last_year + delta_business_value

        return business_value, capital, capital_business, capital_nature, delta_capital, delta_business_value


    def __get_sales_volume_category(self,capital):
        #capital in Mrd Euro

        capi = capital * 1000 #recalc in mio

        if ( capi > 2):
            cat = 'u2'
        else:
            if capi > 10:
                cat = '2-10'
            else:
                if capi > 50:
                    cat = '10-50'
                else:
                    cat = 'o50'


        return cat
    def log_to_journal(self, logId):
        self.journal[logId] = {}
        self.journal[logId]['business_power'] = float(self.business_power)
        self.journal[logId]['co2_emission_total'] = float(self.co2_emission_total)
        self.journal[logId]['count_company'] = int(self.count_company)
        self.journal[logId]['gdp'] = float(self.gdp)
        self.journal[logId]['market_condition'] = float(self.market_condition)
        self.journal[logId]['total_assets'] = float(self.total_assets)
        return self.journal

    def to_dict(self):
        return {
            'business_power': float(self.business_power),
            'co2_emission_total': float(self.co2_emission_total),
            'count_company': int(self.count_company),
            'gdp': float(self.gdp),
            'market_condition': float(self.market_condition),
            'total_assets': float(self.total_assets),
        }