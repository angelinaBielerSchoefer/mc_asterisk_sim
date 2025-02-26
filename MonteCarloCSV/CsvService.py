import re

from WorkItem import WorkItem
from WorkLoad import WorkLoad
from Needle import Needle
from datetime import datetime, timedelta
import random
import csv
import os

class CsvService:    



    def save_mc_result(self, mc_result, start_year=2000, target_year=2031, file_pre="sim4", delimiter=";"):
        dir = "result_data"
        current_date = datetime.now().strftime('%Y%m%d_%H%M')

        name_list = {}
        name_list["capital"] = "capital_to_plot"
        name_list["gdp"] = "gdp_to_plot"

        mc_result['data']['gdp_to_plot'] = mc_result['data']['gdp']
        mc_result['data']['capital_to_plot'] = mc_result['data']['total_assets']

        #name_list["state_of_atmosphere"] = "atmosphere_to_plot"
        #name_list["eco_performance"] = "eco_performance_to_plot"
        #name_list["success"] = "success_to_plot"

        year_row = list(range(start_year, target_year))

        for name in name_list:
            field = name_list[name]
            file_path = os.path.join(dir, '{0}_{1}_{2}.csv'.format(file_pre,current_date,name))
            data={}

            data['year'] = []
            #set column names
            for scenario in mc_result:

                #if scenario != "data":
                column_name = "{0}_{1}".format(name,scenario)
                if not column_name in data:
                    data[column_name] = []

            for year in year_row:
                data['year'].append(year)

                for scenario in mc_result:
                    column_name = "{0}_{1}".format(name,scenario)

                    if year in mc_result[scenario][field]:
                        if not scenario == 'data':
                            data[column_name].append(mc_result[scenario][field][year]['mean'])
                        else:
                            data[column_name].append(mc_result[scenario][field][year])
                    else:
                        data[column_name].append('')
            self.__write_into_file(data, delimiter, file_path)
        return
    def save_mc_result_sim4(self, data_in, tuple, start_year, target_year, current_date = datetime.now().strftime('%Y%m%d_%H%M'), file_pre="sim4", delimiter=";"):
        name_file = tuple[1]
        name_sce = tuple[3]
        unit = tuple[4]
        dir = "result_data_{0}".format(file_pre)
        file_path = os.path.join(dir, '{0}_{1}_{2}.csv'.format(file_pre,current_date,name_file))
        data_out = { 'year' : [],
                     'unit' : []}

        print("target year: {0}".format(target_year))
        year = start_year
        while year <= target_year:
            data_out['year'].append(year)
            data_out['unit'].append(unit)
            for scenario, entry in data_in.items():
                keys=['mean']
                if scenario != 'data':
                    keys.append('min')
                    keys.append('max')
                for key in keys:
                    column = "{0}_{1}_{2}".format(scenario,key, name_sce)
                    if not column in data_out:
                        data_out[column] = []
                    value = ""
                    if year in entry:
                        value = entry[year][key]
                    data_out[column].append(value)
            year +=1
        self.__write_into_file(data_out, delimiter, file_path)
        return

    def __write_into_file(self, data, delimiter, file_path):
        #print (data)

        keys = list(data.keys())  # Spaltennamen (Header)
        with (open(file_path, 'w', encoding='utf-8-sig') as file):
            csv_writer = csv.DictWriter(file, delimiter=delimiter, fieldnames=keys)
            csv_writer.writeheader()
            for i in range(len(data['year'])):

                # Zeile als Dictionary erstellen
                row = {}
                for key, value in data.items():
                    row[key] = value[i]


                csv_writer.writerow(row)
        return
    def read_station_list(self, file_path, delimiter=" "):
        stations =[]
        print("Stations list not yet loaded")
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        storypoints_minutes_map = []

        with open(file_path, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)

            for row in csv_reader:
                var = str(row["stations"])
                stations.append(var)

        print("Loading finalized: {0} datasets out of file {1}".format(len(stations), file_path))

        return stations
    def read_gdp_list(self, delimiter = ";"):
        dataset = {}
        file_path = "sim3_gdp.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):

                    data = row.split(delimiter)
                    year = int(data[2])
                    value = float(data[3]) / 1000000000000 #read in us dollar recalculate in billions
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_ger_gdp_list(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_vgr_ger.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):

                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[10])  #read in mrd euro
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_ger_bvbig_list(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_bv_big_ger.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):

                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[2])/1000  #read in mio euro rcalc in mrd euro
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_grow_rate_list(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_uzw.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[0])
                    value = [float(data[7])] #read values in mio metric ton
                    if not year in dataset and not year == 2019: #2019 wurde die statistische Erfassung von Daten geändert, daher ist die Zuwachsrate nicht berechenbar
                        dataset[year] = value

        return dataset
    def read_carbon_credits_list(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_cc.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[4]) #read values in mio metric ton
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_ger_capbig_list(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_ums_big_ger.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[2])/1000 #read values in millions euro recalc in mrd euro
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_ger_total_assets_list(self, delimiter = ";"):
        dataset = {}
        #file_path = "sim4_ta_ger.csv"
        file_path = "sim4_ums_ger.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[0])
                    value = float(data[5])/ 1000000 #read values in tsd recalculat to mrd euro
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_total_assets_list(self, delimiter = ";"):
        dataset = {}
        file_path = "sim3_ta.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[2])* 1000 #read values in trillions recalculat to billions us dollar
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_state_atmosphere(self, delimiter = ";"):
        dataset = {}
        file_path = "sim3_atmos.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[2]) # ppm
                    if not year in dataset:
                        dataset[year] = value

        return dataset

    def read_ger_co2_emissions(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_co2em_ger.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[5])/ 1000000# metric tone of CO?-eq recalc to mio metric tone
                    if not year in dataset:
                        dataset[year] = value

        return dataset

    def read_global_co2_emissions(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_co2em_glo.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[2])* 1000# billion metric tone of CO?-eq recalc to mio metric tone
                    if not year in dataset:
                        dataset[year] = value

        return dataset

    def read_co2_emissions(self, delimiter = ";"):
        dataset = {}
        file_path = "sim3_co2em.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[2]) #Giga Tonnen Co2 =Gt Co2
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_co2_prices(self, delimiter = ";"):
        dataset = {}
        file_path = "sim3_co2p.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[2]) #U.S. dollars per metric ton of CO₂
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_price_allowances(self,  delimiter = ";"):
        dataset = {}
        file_path = "sim3_co2p.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[2]) / 1000
                    #U.S. dollars per metric ton of CO₂
                    #recalc mrd Euro per mio metric ton

                    if not year in dataset:
                        dataset[year] = value
        return dataset
    def read_price_credits(self,  delimiter = ";"):
        dataset = {}
        file_path = "sim4_ccp.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[0])
                    value = float(data[1]) / 1000 * 0.91
                    #U.S. dollars per metric ton of CO₂
                    #exchange average of 0.91 Euro per US$
                    #recalc mrd Euro per mio metric ton

                    if not year in dataset:
                        dataset[year] = value
        return dataset
    def read_co2_prices_euets(self, delimiter = ";"):
        dataset = {}
        file_path = "sim3_co2p.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[2]) *1000000#U.S. dollars per metric ton of CO₂ recalc US$ per mio metric ton
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_co2_sold_allowances(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_solda_ger.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[5]) / 1000000# metric tone of CO₂-eq recalc to mio metric tone
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_co2_subvention(self, delimiter = ";"):
        dataset = {}
        year = 2008
        while year <2023:
            dataset[year] = random.uniform(1,50) #mrd euro
            year+=1
        file_path = "sim4_sub_ger.csv"
        #print("Loading Items from CSV File: '{0}'.".format(file_path))
        #with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
        #    for row in file:
        #        # Entferne führende und abschließende Leerzeichen (z. B. '\n')
        #        row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
        #        if not row.startswith("#"):
        #            data = row.split(delimiter)
        #            year = int(data[1])
         #           value = float(data[5]) / 1000000# metric tone of CO₂-eq recalc to mio metric tone
        #            if not year in dataset:
        #                dataset[year] = value

        return dataset
    def read_co2_free_allowances(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_freea_ger.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = float(data[5]) / 1000000# metric tone of CO2-eq recalc to mio metric tone
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_co2_prices_eu(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_co2p_eu.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[1])
                    value = (-1) * float(data[2]) #U.S. dollars per metric ton of CO₂
                    if not year in dataset:
                        dataset[year] = value

        return dataset
    def read_investmen_by_categorie(self, delimiter = ";"):
        dataset = {}
        file_path = "sim4_inv.csv"
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split(delimiter)
                    year = int(data[0])
                    cat = str(data[1])
                    value = float(data[2]) / 1000000#read in tsd euro rcalc in mrd euro
                    if not cat in dataset:
                        dataset[cat] = {}
                    if not year in dataset[cat]:
                        dataset[cat][year] = value

        return dataset

    #### SIM 3 Planetary Boundary Masterarbeit
    def read_from_station_file(self, station):
        dataset = {}
        file_path = "co2/co2_{0}_surface-flask_1_ccgg_month.txt".format(station)
        print("Loading Items from CSV File: '{0}'.".format(file_path))
        with open(file_path, "r") as file:
            # Iteriere durch jede Zeile der Datei
            for row in file:
                # Entferne führende und abschließende Leerzeichen (z. B. '\n')
                row = row.strip()
                # Überspringe Zeilen, die mit '#' beginnen
                if not row.startswith("#"):
                    data = row.split()
                    #data_fields: site year month value
                    year = int(data[1])
                    month = int(data[2])
                    value = float(data[3])
                    if not year in dataset:
                        dataset[year] = {}
                    if not month in dataset[year]:
                        dataset[year][month] = value
            #print("Loading finalized: {0} datasets out of file {1}".format(len(dataset), file_path))
        return dataset


    #### SIM 2 Workloads
    def read_workloads(self, file_path, delimiter, story_points_column, time_spend_column, time_format):
        print("Loading Items from CSV File: '{0}'. Column Name '{1}' as int and Column Name '{2}' as Time Format '{3}'".format(file_path, story_points_column, time_spend_column, time_format))
        storypoints_minutes_map = []
        if (time_format == "%d:%d"):
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                csv_reader = csv.DictReader(file, delimiter=delimiter)

                for row in csv_reader:
                    storypoints_raw = row[story_points_column]
                    timespend_raw = row[time_spend_column]

                    if (storypoints_raw != '' and timespend_raw != ''):

                        storypoints = int (storypoints_raw)

                        time = re.split(":", timespend_raw)

                        minutes_spend = (int(time[0])*60) + int(time[1])
                        storypoints_minutes_map.append(WorkLoad(storypoints, minutes_spend))

            print("Loading finalized: {0} datasets out of file {1}".format(len(storypoints_minutes_map), file_path))
        else: print("unknown time format: {0}".format(time_format))
        return storypoints_minutes_map

    #### SIM 1 PI
    def read_needles(self, file_path, delimiter, x_column_name, y_column_name):
        needles = []

        with open(file_path, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)

            for row in csv_reader:
                x_raw = row[x_column_name]
                y_raw = row[y_column_name]

                x = float(x_raw)
                y = float(y_raw)
                needles.append(Needle(x,y))

        print("Found {0} Needle Coordinates in the CSV".format(len(needles)))
        return needles

    #### SIM 0 WorkItem
    def get_closed_items(self, file_path, delimiter, column_name, date_format):
        print("Loading Items from CSV File: '{0}'. Column Name '{1}' and Date Format '{2}'".format(file_path, column_name, date_format))
        work_items = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file, delimiter=delimiter)
            
            for row in csv_reader:
                closed_date_raw = row[column_name]

                if closed_date_raw:
                    closed_date = datetime.strptime(closed_date_raw, date_format)           
                    work_items.append(WorkItem(closed_date))
        
        print("Found {0} Items in the CSV".format(len(work_items)))

        return work_items

    def write_example_file(self, file_path, delimiter, column_name, history, date_format):
        print("Writing Example File with random values to {0}".format(file_path))
        
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=delimiter)
            field = [column_name]
            
            # Write Header
            writer.writerow(field)
            
            # Generate random entries
            for _ in range(30):
                random_days_ago = random.randint(0, history)
                random_date = datetime.now() - timedelta(days=random_days_ago)
                formatted_date = random_date.strftime(date_format)
                writer.writerow([formatted_date])