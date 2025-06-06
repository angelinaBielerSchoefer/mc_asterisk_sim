import argparse
from datetime import datetime, timedelta
import os

#from pycparser.c_ast import Default

from MonteCarloPlanetaryBoundary import MonteCarloPlanetaryBoundary
from MonteCarloMarket import MonteCarloMarket
from MonteCarloService import MonteCarloService
from CsvService import CsvService
from MonteCarloSimWorkLoad import MonteCarloSimWorkLoad
from game import Game


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--FileName", default="")
    parser.add_argument("--Delimiter", default=None)
    parser.add_argument("--Delimeter", default=";")   # For backwards compatibility because I didn't know how to spell this :-)
    parser.add_argument("--ClosedDateColumn", default="Closed Date")
    parser.add_argument("--DateFormat", default="%m/%d/%Y %I:%M:%S %p")
    parser.add_argument("--TargetDate", default="")
    parser.add_argument("--TargetDateFormat", default="%d.%m.%Y")
    parser.add_argument("--RemainingItems", default="10")
    parser.add_argument("--History", default="360")
    parser.add_argument("--SaveCharts", default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument("--SimulationId", default="4")
    ## simID 0 = Simulation der WorkItems sim(remainingItems)= Wann fertig; sim(Verbleibende Tage)= Wieviele Items werden fertig
    ## simID 1 = Simulation für PI Annäherung
    ## simID 2 = Simulation der Workload sim(StoryPoins) = Zeitschätzung zur Fertigstellung; sim(verbleibende Zeit in min) = wieviele Storypoints sind schaffbar
    ## simID 3 = Simulation für Masterarbeit Zustand der Planetaren grenzen nach der Zeit

    parser.add_argument("--NeedleXColumn", default="Needle X")
    parser.add_argument("--NeedleYColumn", default="Needle Y")
    parser.add_argument("--Radius", default="1")
    parser.add_argument("--TargetPrecision", default="0.005")

### SIM 2 Parameter
    parser.add_argument("--StoryPointsColumn", default="Story Points")
    parser.add_argument("--TimeSpendColumn", default="Time Spend")
    parser.add_argument("--TimeSpendFormat", default="%d:%d")
    parser.add_argument("--RemainingMinutes", default="360")
    parser.add_argument("--RemainingStoryPoints", default="10")

    parser.add_argument("--Trials", default="100")
    parser.add_argument("--NumComp", default="2000")
    parser.add_argument("--Run", default="parallel")

    return parser.parse_args()

#### SIM 0 WorkItems
def get_closed_items_history(csv_service, monte_carlo_service, file_name, delimiter, closed_date_column, date_format):
    work_items = csv_service.get_closed_items(file_name, delimiter, closed_date_column, date_format)
    closed_items_history = monte_carlo_service.create_closed_items_history(work_items)
    return closed_items_history

#### SIM 1 PI Needles
def get_needle_datasets(csv_service, monte_carlo_service, file_name, delimiter, needle_x_column, needle_y_column, radius=1.0, square_side=2.0):
    needles = csv_service.read_needles(file_name, delimiter, needle_x_column, needle_y_column)
    monte_carlo_service.initPiSim(len(needles), radius, square_side)
    needles_datasets = monte_carlo_service.prepare_pi_simulation(needles)
    return needles_datasets

#### SIM 2 Workload
def get_workload_datasets(csv_service, monte_carlo_sim_workload, file_name, delimiter, story_point_column, time_spend_column, time_spend_format):
    storypoints_minutes_map = csv_service.read_workloads(file_name, delimiter, story_point_column, time_spend_column, time_spend_format)
    monte_carlo_sim_workload.initWorkLoadSim(len(storypoints_minutes_map))
    storypoints_per_minute, minutes_per_storypoint, stratified_by_storypoint = monte_carlo_sim_workload.create_workload_occurance(storypoints_minutes_map)
    print("-----------------------------------------")
    print("Following data base prepared")
    print("-----------------------------------------")
    print("--- Data for Simulation: How Many Storypoint are finalized in given remaining time?")
    print("Story Points per Minute: {0}".format(storypoints_per_minute))

    print("--- Data for Simulation: When (How many hours/days) will a given number of Storypoints need to be finalized?")
    print("Minutes per Story Point: {0}".format(minutes_per_storypoint))

    print("--- Data for Simulation: When (How many hours/days) will a given number of Tickets with estimated Storypoints need to be finalized?")
    print("Stratified by Story Points: {0}".format(stratified_by_storypoint))
    #print("Story Points Minutes Map: {0}".format(storypoints_minutes_map))
    print("-----------------------------------------")

    return storypoints_per_minute, minutes_per_storypoint, stratified_by_storypoint

#### SIM 3 Masterarbeit
def get_station_year_month_value(csv_service, file_name):
    station_shortcuts = csv_service.read_station_list(file_name)
    datasets={}
    for station in station_shortcuts:
        datasets[station] = csv_service.read_from_station_file(station)
    return datasets
def get_gdp_year_value(csv_service):
    datasets = csv_service.read_gdp_list()
    return datasets
def get_ger_gdp_year_value(csv_service):
    datasets = csv_service.read_ger_gdp_list()
    return datasets
def get_ger_bvbig_year_value(csv_service):
    datasets = csv_service.read_ger_bvbig_list()
    return datasets
def get_ger_capbig_year_value(csv_service):
    datasets = csv_service.read_ger_capbig_list()
    return datasets
def get_carbon_credit_year_value(csv_service):
    datasets = csv_service.read_carbon_credits_list()
    return datasets
def get_grow_rate_year_value(csv_service):
    dataset = csv_service.read_grow_rate_list()
    return dataset
def get_ger_total_assets_year_value(csv_service):
    datasets = csv_service.read_ger_total_assets_list()
    return datasets
def get_total_assets_year_value(csv_service):
    datasets = csv_service.read_total_assets_list()
    return datasets
def get_atmospheric_state_year_value(csv_service):
    datasets = csv_service.read_state_atmosphere()
    return datasets
def get_ger_co2_emissions_year_value(csv_service):
    datasets = csv_service.read_ger_co2_emissions()
    return datasets
def get_global_co2_emissions_year_value(csv_service):
    datasets = csv_service.read_global_co2_emissions()
    return datasets
def get_co2_emissions_year_value(csv_service):
    datasets = csv_service.read_co2_emissions()
    return datasets
def get_co2_free_allowances_value(csv_service):
    dataset = csv_service.read_co2_free_allowances()
    return dataset
def get_co2_sold_allowances_value(csv_service):
    dataset = csv_service.read_co2_sold_allowances()
    return dataset
def get_co2_subvention_value(csv_service):
    dataset= csv_service.read_co2_subvention()
    return dataset
def get_co2_price_year_value(csv_service):
    dataset = csv_service.read_co2_prices()
    return dataset
def get_co2_price_euets_year_value(csv_service):
    dataset = csv_service.read_co2_prices_euets()
    return dataset
def get_price_credits_year_value(csv_service):
    dataset = csv_service.read_price_credits()
    return dataset
def get_price_allowances_year_value(csv_service):
    dataset = csv_service.read_price_allowances()
    return dataset
def get_investment_compcat_year_value(csv_service):
    dataset = csv_service.read_investmen_by_categorie()
    return dataset
def print_logo():
    logo = r"""
     /$$                 /$$           /$$$$$$$                           /$$                /$$      /$$                  /$$      
    | $$                | $$          | $$__  $$                         | $$               | $$  /$ | $$                 | $$      
    | $$       /$$$$$$ /$$$$$$        | $$  \ $$/$$$$$$  /$$$$$$  /$$$$$$| $$ /$$$$$$       | $$ /$$$| $$ /$$$$$$  /$$$$$$| $$   /$$
    | $$      /$$__  $|_  $$_/        | $$$$$$$/$$__  $$/$$__  $$/$$__  $| $$/$$__  $$      | $$/$$ $$ $$/$$__  $$/$$__  $| $$  /$$/
    | $$     | $$$$$$$$ | $$          | $$____| $$$$$$$| $$  \ $| $$  \ $| $| $$$$$$$$      | $$$$_  $$$| $$  \ $| $$  \__| $$$$$$/ 
    | $$     | $$_____/ | $$ /$$      | $$    | $$_____| $$  | $| $$  | $| $| $$_____/      | $$$/ \  $$| $$  | $| $$     | $$_  $$ 
    | $$$$$$$|  $$$$$$$ |  $$$$/      | $$    |  $$$$$$|  $$$$$$| $$$$$$$| $|  $$$$$$$      | $$/   \  $|  $$$$$$| $$     | $$ \  $$
    |________/\_______/  \___/        |__/     \_______/\______/| $$____/|__/\_______/      |__/     \__/\______/|__/     |__/  \__/
                                                                | $$                                                                
                                                                | $$                                                                
                                                                |__/                                                                
    """
    print(logo)

def check_if_file_exists(file_path, raise_if_not_found = False):
    if not os.path.isfile(file_path):
        if raise_if_not_found:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        
        return False
    
    return True

#def check_for_updates(package_name):
    #try:
        #current_version = version(package_name)

        # Query PyPI for the latest version
        #response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        #response.raise_for_status()
        #latest_version = response.json()["info"]["version"]

        # Compare versions
        #if current_version != latest_version:
        #    print("------- Update Available -----------")
        #    print(f"Update available: {latest_version} (current: {current_version})")
        #    print(f"Run the following command to upgrade: 'python -m pip install --upgrade {package_name}'")
        #    print("------- Update Available -----------")

    #except Exception:
    #    print("Error checking for updates - ignoring")

def main():    
    try:

        #### general argument Parsing
        args = parse_arguments()
        simId = int(args.SimulationId)
        print("######### SIMULATIONID {0} #########".format(simId))
        file_name = args.FileName
        # Use the proper spelling if anything is defined. If not, we either use the old wrong spelling or we take the default (as it wasn't defined at all)
        delimiter = args.Delimiter if args.Delimiter else args.Delimeter

        #### python consolen parameter aufnehmen
        match simId:
            case 0:
                ########## intern_sim0_parameterParsing
                print("######### SIMULATION of WorkItems #########")
                remaining_items = int(args.RemainingItems)
                ### Datenpool Zugriff für Workitems: Bestimme den Bezugszeitraum
                history = try_parse_int(args.History)
                if history:
                    print("Use rolling history of the last {0} days".format(history))
                else:
                    history_start = datetime.strptime(args.History, "%Y-%m-%d").date()
                    today = datetime.today().date()
                    history = (today - history_start).days
                    print("Using history with fixed start date {0} - History is {1} days".format(history_start, history))
                ### Datenformat und Spaltenname für Fertigstellungsdatum zum Einlesen
                closed_date_column = args.ClosedDateColumn
                date_format = args.DateFormat
            case 1:
                ########## intern_sim1_parameterParsing
                print("######### SIMULATION of PI #########")
                # Datenpool Zugriff für PI:
                x_column = args.NeedleXColumn
                y_column = args.NeedleYColumn
                radius = int(args.Radius)
                square_side= 2* radius
            case 2:
                ########## intern_sim2_parameterParsing
                print("######### SIMULATION of WorkLoad #########")
                # Datenpoolzugriff für Workload:
                story_points_column = args.StoryPointsColumn
                time_spend_column = args.TimeSpendColumn

                time_format = args.TimeSpendFormat
                date_format = args.DateFormat

                remainingMinutes = args.RemainingMinutes
                remainingStoryPoints = args.RemainingStoryPoints
            case 3:
                ########## intern_sim3_parameterParsing
                print( "######## SIMULATION of Planetary Boundaries ########")
                start_year = 2022
                target_year = 2030
                pb_name = "atmosphere"
                station_shortcuts = ["abp","alt","ams"]
            case 4:
                print( "######## SIMULATION of Co2 Market ########")
                numComp = args.NumComp
                run_mode = args.Run
                start_year = 2008
                target_year = 2050
                trials = args.Trials
                pb_name = "atmosphere"
                assume = {
                    'prices_lower_limit': float(0.8),
                    #https://wiki.bildungsserver.de/klimawandel/index.php/Kohlendioxid-Konzentration
                    #  1 ppm CO2 = 7,814 Gt CO2
                    # co2_em given in mio metric tones CO2
                    # atmospheric state given in ppm CO2
                    #r_convert = 7814
                    'r_convert': 7814, #
                    'stdev_business_power': float(0.188),#0.188 stdev of business power over the year
                    'stdev_delta_co2_intensity': float(0.012),#Randomly chosen
                    'stdev_market_influence': float(0.018),#0.018 stdev of marketconditions over the years
                    'stdev_start_assets': float(2.9),##2,9 stdev of data total assets over the years
                    'stdev_start_invest': float(1.0),
                    'stdev_start_co2_emission': float(2),#random set
                    'stdev_start_co2_intensity': float(6.23314),#standard deviation taken from Co2-intensity deviation by sector: https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Umwelt/UGR/_Grafik/_Interaktiv/co2-emissionsintensitaet.html
                    'stdev_start_value': float(666), ##666 stdev of data gdp over the years
                }
            case 5:
                numComp = args.NumComp
                run_mode = args.Run
                start_year = 2008
                target_year = 2030
                trials = args.Trials
                assume = {}
            case _:
                print("Unknown SimId")
                exit()


        #### generelle Vorbereitung CSVService und MonteCarloService
        csv_service = CsvService()

        #### Input variables: Define Preconditions of Monte Carlo
        match simId:
            case 0:
                ######### intern_sim0_setupInputMC
                monte_carlo_service = MonteCarloService(args.SaveCharts, trials)
                target_date = (datetime.now() + timedelta(days=14)).date()
                if args.TargetDate:
                    target_date = datetime.strptime(args.TargetDate, args.TargetDateFormat).date()
                monte_carlo_service.initWorkItemSim(history)
            case 1:
                ######### intern_sim1_setupInputMC
                monte_carlo_service = MonteCarloService(args.SaveCharts, trials)
                monte_carlo_service.setPrecision(float(args.TargetPrecision))
            case 2:
                ######### intern_sim2_setupInputMC
                #print( "Input variables of Workload")
                monte_carlo_sim_workload = MonteCarloSimWorkLoad(args.SaveCharts, trials)
                #monte_carlo_sim_workload.prepare_workload_simulation()
            case 3:
                ######### intern_sim3_setupInputMC
                #print( "Input variables of Planetary Boundary Simulation")
                monte_carlo_pb = MonteCarloPlanetaryBoundary()

            case 4:
                ######### intern_sim4_setupInputMC
                parallel = False
                if run_mode =="parallel":
                    parallel = True

                monte_carlo_mkt = MonteCarloMarket(int(trials),
                                                   int(numComp),
                                                   assume=assume,
                                                   parallel=parallel,
                                                   start_year = start_year
                                                   )
            case 5:
                parallel = False
                if run_mode =="parallel":
                    parallel = True
                simulation_game = Game(int(trials),
                                       int(numComp),
                                       assume=assume,
                                       parallel = parallel,
                                       start_year = start_year,
                                       target_year = target_year)


        #### Print: good to know
        print("================================================================")
        print("Starting montecarlocsv with following Parameters for CSV loading:")
        print("================================================================")
        print("FileName: {0}".format(file_name))
        print("Delimiter: {0}".format(delimiter))
        match simId:
            case 4:
                print("Start Year: {0}".format(start_year))
                print("Target Year: {0}".format(target_year))
                print("Count Company: {0}".format(numComp))
                print("Count Trials: {0}".format(trials))
                print("Assumptions: {0}".format(assume))
            case 5:
                print("Start Year: {0}".format(start_year))
                print("Target Year: {0}".format(target_year))
                print("Assumptions: {0}".format(assume))


        print("Save Charts: {0}".format(args.SaveCharts))
        print("----------------------------------------------------------------")

        #### general File Check
        if file_name == '':
            print("No csv file specified - generating example file with random values")
            file_name = os.path.join(os.getcwd(), "ExampleFile.csv")
            if not check_if_file_exists(file_name):
                csv_service.write_example_file(file_name, delimiter, closed_date_column, history, date_format)

        #### Datensätze laden
        match simId:
            case 4:
                print( "Read Datasets in CSV")
                print( "not yet implemented")
                data_atmosphere_year_value = get_atmospheric_state_year_value(csv_service)

                data_gdp_year_value = get_ger_gdp_year_value(csv_service)
                data_bvbig_year_value = get_ger_bvbig_year_value(csv_service)
                data_capbig_year_value = get_ger_capbig_year_value(csv_service)
                data_carbon_credits_year_value = get_carbon_credit_year_value(csv_service)
                data_total_assets_year_value = get_ger_total_assets_year_value(csv_service)
                data_company_grow_rate_year_value = get_grow_rate_year_value(csv_service)
                data_emissions_year_value = get_ger_co2_emissions_year_value(csv_service)
                data_investment_by_category_year_value = get_investment_compcat_year_value(csv_service)
                #data_co2_price_year_value = get_co2_price_euets_year_value(csv_service)
                data_co2_emission_global_year_value = get_global_co2_emissions_year_value(csv_service)
                data_co2_free_allowances_value = get_co2_free_allowances_value(csv_service)
                data_co2_price_year_value = get_co2_price_year_value(csv_service)
                data_co2_sold_allowances_value = get_co2_sold_allowances_value(csv_service)
                data_co2_subvention_value = get_co2_subvention_value(csv_service)
                data_price_allowances_year_value = get_price_allowances_year_value(csv_service)
                data_price_credit_year_value = get_price_credits_year_value(csv_service)
            case 5:
                data_gdp_year_value = get_ger_gdp_year_value(csv_service)
                data_capital_year_value = get_ger_total_assets_year_value(csv_service)
                data = (data_capital_year_value,
                        data_gdp_year_value)

        #### SIMULATION execution

        print("=========================================")
        print("EXECUTE SIMULATION")
        print("=========================================")

        match simId:
            case 4:
                #### intern_sim_4_simulateMC()
                print( "Simulation execution of state of Co2 Market")
                print("implementation ongoing")
                mc_result, sig_result = monte_carlo_mkt.start_simulation(data_atmosphere_year_value,
                                                                         data_bvbig_year_value,
                                                                         data_capbig_year_value,
                                                                         data_carbon_credits_year_value,
                                                                         data_co2_emission_global_year_value,
                                                                         data_co2_free_allowances_value,
                                                                         data_co2_price_year_value,
                                                                         data_co2_sold_allowances_value,
                                                                         data_co2_subvention_value,
                                                                         data_company_grow_rate_year_value,
                                                                         data_emissions_year_value,
                                                                         data_gdp_year_value,
                                                                         data_investment_by_category_year_value,
                                                                         data_price_allowances_year_value,
                                                                         data_price_credit_year_value,
                                                                         data_total_assets_year_value,
                                                                         pb_name,
                                                                         )
            case 5:
                print( "Simulation execution of state of Scenario 1 and 2")
                print("implementation ongoing")
                sc1_result, sc2_result = simulation_game.start_simulation(data)

                data = [123,159,258]

                #print("ist sc1 result:", sc1_result)
                #sc1_result = ([102,150,200], [125, 169, 240], [170,210,300])
                #print("soll sc1 result:", sc1_result)

                sc2_result = ([98,148,180], [98,148,180], [98,148,180])
        #### intern_sim0_printResults():
        print()
        print("================================================================")
        print("Summary")
        print("================================================================")
        print()
        match simId:
            case 3:

                csv_service.save_mc_result(mc_result)
                monte_carlo_pb.plot_them_all(mc_result)
                year = start_year-1

                mu_suc_measured = sig_result['val_suc_model'][year]['mu_suc_data']
                mu_suc_sc1 = sig_result['val_suc_model'][year]['mu_suc_sc1']


                print("SC 1: Validity of Simulation Modelling Success")
                print("Base Calculation Success = gdp increase rate = Delta_GDP[year]/GDP[year-1]")
                print()
                print("Success ({0}) by measured: {1}".format(year,mu_suc_measured))
                print("Success ({0}) by simulation 1: {1}".format(year,mu_suc_sc1))
                print("Validation of H0 ({0})".format(sig_result['val_suc_model'][year]['H0_suc']))
                print("Expectation {0}: was proven {1}".format(sig_result['val_suc_model'][year]['expected'],sig_result['val_suc_model'][year]['accept_H0']))
                print("Acceptance of alternative H1 ({0}) is {1}".format(sig_result['val_suc_model'][year]['H1_suc'],sig_result['val_suc_model'][year]['accept_H1']))
                print()
                print("----------------------------------------")
                mu_ecoP_measured = sig_result['val_eco_model'][year]['mu_eco_sc1']
                mu_ecoP_sc2 = sig_result['val_eco_model'][year]['mu_eco_sc2']

                print("SC 2: Validity of Simulation Modelling ecologic Performance: ecoPerformance = f(Planetary_State, invested_Capital)")
                print("SC 2: Validity check of Scaling of ecologic Performance")
                print("Calculation change of Success: Delta_GDP[year]/GDP[year-1] + ecoPerformance")
                print()
                print("Ecologic Performance ({0}) by measured: {1}".format(year,mu_ecoP_measured))
                print("Ecologic Performance ({0}) by simulation 2: {1}".format(year,mu_ecoP_sc2))
                print("Validation of H0 ({0})".format(sig_result['val_eco_model'][year]['H0_eco']))
                print("Expectation {0}: was proven {1}".format(sig_result['val_eco_model'][year]['expected_eco'],sig_result['val_eco_model'][year]['accept_H0_eco']))
                print("Expected state of atmosphere in {0}: {1}".format(year,sig_result['val_eco_model'][year]['state_of_atmosphere']))
                print("Acceptance of alternative H1 ({0}) is {1}".format(sig_result['val_eco_model'][year]['H1_eco'],sig_result['val_eco_model'][year]['accept_H1_eco']))
                print()

                mu_suc_sc1 = sig_result['val_eco_model'][year]['mu_suc_sc1']
                mu_suc_sc2 = sig_result['val_eco_model'][year]['mu_suc_sc2']

                print("Success ({0}) by simulation 1: {1}".format(year,mu_suc_sc1))
                print("Success ({0}) by simulation 2: {1}".format(year,mu_suc_sc2))
                print("Validation of H0 ({0})".format(sig_result['val_eco_model'][year]['H0_suc']))
                print("Expectation {0}: was proven {1}".format(sig_result['val_eco_model'][year]['expected_suc'],sig_result['val_eco_model'][year]['accept_H0_suc']))
                print("Acceptance of alternative H1 ({0}) is {1}".format(sig_result['val_eco_model'][year]['H1_suc'],sig_result['val_eco_model'][year]['accept_H1_suc']))


                year = target_year
                print()
                print()
                print("----------------------------------------")
                print("SC 3: Optimization of Success: optimize weight of capital requirement for gdp increase rate and ecological performance")
                mu_ecoP_sc3 = sig_result['proof_impact'][year]['mu_eco_sc3']
                mu_ecoP_sc2 = sig_result['proof_impact'][year]['mu_eco_sc2']
                mu_suc_sc3 = sig_result['proof_impact'][year]['mu_suc_sc3']
                print()
                print("Ecologic Performance ({0}) by Scenario 2: {1}".format(year,mu_ecoP_sc2))
                print("Ecologic Performance ({0}) by Scenario 3: {1}".format(year,mu_ecoP_sc3))
                print("|z_eco_test|>z_between_min_max: {0}>{1})".format(sig_result['proof_impact'][year]['z_eco_test'], sig_result['proof_impact'][year]['z_between_min_max']))
                print("Validation of H0 ({0})".format(sig_result['proof_impact'][year]['H0_eco']))
                print("Expectation {0} for test variable {1}: was proven {2}".format(sig_result['proof_impact'][year]['expected_eco'],
                                                                                     sig_result['proof_impact'][year]['test_variable_eco'],
                                                                                     sig_result['proof_impact'][year]['accept_H0_eco']))
                print("Expected state of atmosphere in {0}: {1}".format(year,sig_result['proof_impact'][year]['state_of_atmosphere']))
                print("Acceptance of alternative H1 ({0}) is {1}".format(sig_result['proof_impact'][year]['H1_eco'],sig_result['proof_impact'][year]['accept_H1_eco']))
                print()


                print("### old ### Calculation change of Success: Delta_GDP[year]/GDP[year-1] + ecoPerformance")
                print()
                print("Ecologic Performance ({0}) by simulation 2: {1}".format(year,mu_ecoP_sc2))
                print("Ecologic Performance ({0}) by simulation 3: {1}".format(year,mu_ecoP_sc3))
                print("Significant Difference in ecoPerformance: TRUE/FALSE (expected sign diff to proof that ecoPerformance changes when more capital is invested)")
                print()
                print("Success ({0}) by simulation 2: {1}".format(year,mu_suc_sc2))
                print("Success ({0}) by simulation 3: {1}".format(year,mu_suc_sc3))
                print("Significant Difference in success: TRUE/FALSE (expected no diff to proof that investment into ecoPerformance would crash business cases)")
                print()
            case 4:
                print("ongoing ....")
                monte_carlo_mkt.plot_results(mc_result, csv_service)
            case 5:
                simulation_game.plot_results(data, sc1_result, sc2_result, csv_service)
        print()
        print("================================================================")
        print("Simulation {0} Terminated".format(simId))
        print("================================================================")
        
    except Exception as exception:
        print("Error while executing montecarloscsv:")
        print(exception)
        
        #print("🪲 If the problem cannot be solved, consider opening an issue on GitHub: https://github.com/LetPeopleWork/MonteCarloCSV/issues 🪲")


def try_parse_int(value):
    try:
        return int(value)
    except ValueError:
        return None







if __name__ == "__main__":
    main()