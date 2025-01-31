
class Company:
    def __init__(self, business_value_start,
                 capital_start,
                 weight_nature):
        self.business_value = business_value_start
        self.capital = capital_start  # mrd euro
        self.capital_nature = weight_nature * self.capital
        self.capital_business = self.capital-self.capital_nature
        self.weight_business = 1- weight_nature
        self.weight_nature =  weight_nature

        self.co2_emission_idle = 0.0
        self.co2_intensity = 0.0 # tons per 1000 euro business_value
        self.co2_emission = 0.0
        self.co2_demand = 37.54
        self.co2_supply = 0

        self.business_power = 0.0
        self.market_influence = 0.0
        self.is_alive = True
