'''
afhsb_csv.py creates CSV files 
1) filled_00to13.csv
2) filled_13to17.csv
3) state2region.csv 
4) simple_DMISID_FY2018.csv
These files will be later used to create MYSQL data tables. 

Several intermediate files will be created, including:
00to13.pickle  13to17.pickle 00to13.csv 13to17.csv

Required source files under SOURCE_DIR:
1) ili_1_2000_5_2013_new.sas7bdat 
2) ili_1_2013_11_2017_new.sas7bdat
3) country_codes.csv
4) DMISID_FY2018.csv
All intermediate files and final csv files will be stored in afhsb_utils.TARGET_DIR
'''
# standard library
import csv
import os

# third party
import sas7bdat
import pickle
import epiweeks as epi

# first party
from .dx_fn import DXFN_DICT
from .afhsb_utils import FN_NAME, SOURCE_DIR, TARGET_DIR

DX_FN = DXFN_DICT[FN_NAME]
if (not os.path.exists(TARGET_DIR)): os.makedirs(TARGET_DIR)

def row2epiweek(row, get_field):
	date = get_field(row, 'd_event')
	year, month, day = date.year, date.month, date.day
	week_tuple = epi.Week.fromdate(year, month, day).weektuple()
	year, week_num = week_tuple[0], week_tuple[1]
	return year, week_num

def get_dx_list(row, get_field):
	"""Get non-blank dx1..dx8 diagnosis codes from a row as a list.

	Returns:
		:obj:`list`: List of codes (expected to be strings) with length equal to
		  the number of non-blank entries (max length of 8).
	 """
	dx_list = []
	for i in range(1, 9):
		dx = get_field(row, "dx{}".format(i))
		if (dx == ""): break
		dx_list.append(dx)
	return dx_list

def aggregate_data(sourcefile, targetfile, max_rows=None):
	print("Aggregate {}".format(sourcefile))
	reader = sas7bdat.SAS7BDAT(os.path.join(SOURCE_DIR, sourcefile), skip_header=True) 
	# map column names to column indices
	COL2IDX = {column.name.decode('utf-8'): column.col_id for column in reader.columns}
	def get_field(row, column): return row[COL2IDX[column]]

	results_dict = dict()
	for r, row in enumerate(reader):
		# Read a maximum of max_rows rows:
		if (max_rows is not None and r >= max_rows): break
		# Record only outpatient events:
		if (get_field(row, 'type') != "Outpt"): continue
		
		year, week_num = row2epiweek(row, get_field)
		dmisid = get_field(row, 'DMISID')
		
		dx_list = get_dx_list(row, get_field)
		dx_label = DX_FN(dx_list)

		key_list = [year, week_num, dmisid, dx_label]
		curr_dict = results_dict
		for i, key in enumerate(key_list):
			if (i == len(key_list) - 1):
				if (not key in curr_dict): curr_dict[key] = 0
				curr_dict[key] += 1
			else:
				if (not key in curr_dict): curr_dict[key] = dict()
				curr_dict = curr_dict[key]

	results_path = os.path.join(TARGET_DIR, targetfile)
	with open(results_path, 'wb') as f:
		pickle.dump(results_dict, f, pickle.HIGHEST_PROTOCOL)
	return


################# Functions for geographical information ####################

def get_country_mapping():
	filename = "country_codes.csv"
	mapping = dict()
	with open(os.path.join(SOURCE_DIR, filename), "r") as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			print(row.keys())
			alpha2 = row['alpha-2']
			alpha3 = row['alpha-3']
			mapping[alpha2] = alpha3

	return mapping

def format_dmisid_csv(filename, target_name):
	src_path = os.path.join(SOURCE_DIR, "{}.csv".format(filename))
	dst_path = os.path.join(TARGET_DIR, target_name)

	src_csv = open(src_path, "r", encoding='utf-8-sig')
	reader = csv.DictReader(src_csv)
	
	dst_csv = open(dst_path, "w")
	fieldnames = ['dmisid', 'country', 'state', 'zip5']
	writer = csv.DictWriter(dst_csv, fieldnames=fieldnames)
	writer.writeheader()

	country_mapping = get_country_mapping()

	for row in reader:
		country2 = row['Facility ISO Country Code']
		if (country2 == ""): country3 = ""
		elif (not country2 in country_mapping): 
			for key in row.keys(): print(key, row[key])
			continue
		else:
			country3 = country_mapping[country2]
		new_row = {'dmisid': row['DMIS ID'],
					'country': country3,
					'state': row['Facility State Code'],
					'zip5': row['Facility 5-Digit ZIP Code']}
		writer.writerow(new_row)

def dmisid():
	filename = 'DMISID_FY2018'
	target_name = "simple_DMISID_FY2018.csv"
	format_dmisid_csv(filename, target_name)

cen2states = {'cen1': {'CT', 'ME', 'MA', 'NH', 'RI', 'VT'},
            'cen2': {'NJ', 'NY', 'PA'},
            'cen3': {'IL', 'IN', 'MI', 'OH', 'WI'},
            'cen4': {'IA', 'KS', 'MN', 'MO', 'NE', 'ND', 'SD'},
            'cen5': {'DE', 'DC', 'FL', 'GA', 'MD', 'NC', 'SC', 'VA', 'WV'},
            'cen6': {'AL', 'KY', 'MS', 'TN'},
            'cen7': {'AR', 'LA', 'OK', 'TX'},
            'cen8': {'AZ', 'CO', 'ID', 'MT', 'NV', 'NM', 'UT', 'WY'},
            'cen9': {'AK', 'CA', 'HI', 'OR', 'WA'}}

hhs2states = {'hhs1': {'VT', 'CT', 'ME', 'MA', 'NH', 'RI'},
            'hhs2': {'NJ', 'NY'},
            'hhs3': {'DE', 'DC', 'MD', 'PA', 'VA', 'WV'},
            'hhs4': {'AL', 'FL', 'GA', 'KY', 'MS', 'NC', 'TN', 'SC'},
            'hhs5': {'IL', 'IN', 'MI', 'MN', 'OH', 'WI'},
            'hhs6': {'AR', 'LA', 'NM', 'OK', 'TX'},
            'hhs7': {'IA', 'KS', 'MO', 'NE'},
            'hhs8': {'CO', 'MT', 'ND', 'SD', 'UT', 'WY'},
            'hhs9': {'AZ', 'CA', 'HI', 'NV'},
            'hhs10': {'AK', 'ID', 'OR', 'WA'}}

def state2region(D):
    results = dict()
    for region in D.keys():
        states = D[region]
        for state in states:
            assert(not state in results)
            results[state] = region
    return results

def state2region_csv():
	to_hhs = state2region(hhs2states)
	to_cen = state2region(cen2states)
	states = to_hhs.keys()
	target_name = "state2region.csv"
	fieldnames = ['state', 'hhs', 'cen']
	with open(os.path.join(TARGET_DIR, target_name), "w") as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		for state in states:
			content = {"state": state, "hhs": to_hhs[state], "cen": to_cen[state]}
			writer.writerow(content)

################# Functions for geographical information ####################

######################### Functions for AFHSB data ##########################

def write_afhsb_csv(period):
	flu_mapping = {0: "ili-flu3", 1: "flu1", 2:"flu2-flu1", 3: "flu3-flu2"}
	results_dict = pickle.load(open(os.path.join(TARGET_DIR, "{}.pickle".format(period)), 'rb'))

	fieldnames = ["id", "epiweek", "dmisid", "flu_type", "visit_sum"]
	with open(os.path.join(TARGET_DIR, "{}.csv".format(period)), 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		
		i = 0
		for year in sorted(results_dict.keys()):
			year_dict = results_dict[year]
			for week in sorted(year_dict.keys()):
				week_dict = year_dict[week]
				for dmisid in sorted(week_dict.keys()):
					dmisid_dict = week_dict[dmisid]
					for flu in sorted(dmisid_dict.keys()):
						visit_sum = dmisid_dict[flu]
						i += 1
						epiweek = int("{}{:02d}".format(year, week))
						flu_type = flu_mapping[flu]
						
						row = {"epiweek": epiweek, "dmisid": None if (not dmisid.isnumeric()) else dmisid, 
							"flu_type": flu_type, "visit_sum": visit_sum, "id": i}
						writer.writerow(row)
						if (i % 100000 == 0): print(row)

def dmisid_start_time_from_file(filename):
	starttime_record = dict()
	with open(filename, 'r') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			dmisid = row['dmisid']
			epiweek = int(row['epiweek'])
			if (not dmisid in starttime_record): 
				starttime_record[dmisid] = epiweek
			else:
				starttime_record[dmisid] = min(epiweek, starttime_record[dmisid])
	return starttime_record

def dmisid_start_time():
	record1 = dmisid_start_time_from_file(os.path.join(TARGET_DIR, "00to13.csv"))
	record2 = dmisid_start_time_from_file(os.path.join(TARGET_DIR, "13to17.csv"))
	record = record1
	for dmisid, epiweek in record2.items():
		if (dmisid in record):
			record[dmisid] = min(record[dmisid], epiweek)
		else:
			record[dmisid] = epiweek
	return record

def fillin_zero_to_csv(period, dmisid_start_record):
	src_path = os.path.join(TARGET_DIR, "{}.csv".format(period))
	dst_path = os.path.join(TARGET_DIR, "filled_{}.csv".format(period))

	# Load data into a dictionary
	src_csv = open(src_path, "r")
	reader = csv.DictReader(src_csv)

	results_dict = dict() # epiweek -> dmisid -> flu_type: visit_sum
	for i, row in enumerate(reader):
		epiweek = int(row['epiweek'])
		dmisid = row['dmisid']
		flu_type = row['flu_type']
		visit_sum = row['visit_sum']
		if (not epiweek in results_dict):
			results_dict[epiweek] = dict()
		week_dict = results_dict[epiweek]
		if (not dmisid in week_dict):
			week_dict[dmisid] = dict()
		dmisid_dict = week_dict[dmisid]
		dmisid_dict[flu_type] = visit_sum

	# Fill in zero count records
	dmisid_group = dmisid_start_record.keys()
	flutype_group = ["ili-flu3", "flu1", "flu2-flu1", "flu3-flu2"]

	for epiweek in results_dict.keys():
		week_dict = results_dict[epiweek]
		for dmisid in dmisid_group:
			start_week = dmisid_start_record[dmisid]
			if (start_week > epiweek): continue

			if (not dmisid in week_dict):
				week_dict[dmisid] = dict()

			dmisid_dict = week_dict[dmisid]
			for flutype in flutype_group:
				if (not flutype in dmisid_dict):
					dmisid_dict[flutype] = 0

	# Write to csv files
	dst_csv = open(dst_path, "w")
	fieldnames = ["id", "epiweek", "dmisid", "flu_type", "visit_sum"]
	writer = csv.DictWriter(dst_csv, fieldnames=fieldnames)
	writer.writeheader()

	i = 1
	for epiweek in results_dict:
		for dmisid in results_dict[epiweek]:
			for flutype in results_dict[epiweek][dmisid]:
				visit_sum = results_dict[epiweek][dmisid][flutype]
				row = {"id": i, "epiweek": epiweek, "dmisid": dmisid,
						"flu_type": flutype, "visit_sum": visit_sum}
				writer.writerow(row)
				if (i % 100000 == 0):
					print(row)
				i += 1
	print("Wrote {} rows".format(i))

######################### Functions for AFHSB data ##########################

def explore(period):
	total_count = 0
	results_dict = pickle.load(open(os.path.join(TARGET_DIR, "{}.pickle".format(period)), 'rb'))
	for year in results_dict:
		year_dict = results_dict[year]
		for week in year_dict:
			week_dict = year_dict[week]
			for dmisid in week_dict:
				dmisid_dict = week_dict[dmisid]
				for flu in dmisid_dict:
					total_count += dmisid_dict[flu]
	print("period {} has total observations={}".format(period, total_count))

def check_target_files():
	for filename in ['filled_00to13.csv', 'filled_13to17.csv', 
		'state2region.csv', 'simple_DMISID_FY2018.csv']:
		path = os.path.join(TARGET_DIR, filename)
		if (not os.path.exists(path)): return False
	return True

def check_source_files():
	for filename in ['ili_1_2000_5_2013_new.sas7bdat', 'ili_1_2013_11_2017_new.sas7bdat',
		'country_codes.csv', 'DMISID_FY2018.csv']:
		path = os.path.join(SOURCE_DIR, filename)
		if (not os.path.exists(path)):
			raise Exception("Source file {} doesn't exist. "
			"Cannot create all target files.".format(path))

def aggregate_and_process(max_rows_per_file=None):
	if (check_target_files()):
		print("All target files have been created.")
		return
	check_source_files()

	# Build tables containing geographical information
	state2region_csv()
	dmisid()

	# Aggregate raw data into pickle files
	aggregate_data("ili_1_2000_5_2013_new.sas7bdat", "00to13.pickle", max_rows=max_rows_per_file)
	aggregate_data("ili_1_2013_11_2017_new.sas7bdat", "13to17.pickle", max_rows=max_rows_per_file)

	# write pickle content to csv files
	write_afhsb_csv("00to13")
	write_afhsb_csv("13to17")

	# Fill in zero count records
	dmisid_start_record = dmisid_start_time()
	fillin_zero_to_csv("00to13", dmisid_start_record)
	fillin_zero_to_csv("13to17", dmisid_start_record)


if __name__ == '__main__':
	aggregate_and_process()
	