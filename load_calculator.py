import csv
import datetime
import get_time
import menu

def streamflow_index(header):
	'''returns index of streamflow parameter from header row of site data'''
	streamflow_aliases = ["Streamflow, ft&#179;/s", "Streamflow, ft^3/s"]
	
	for alias in streamflow_aliases:
		if alias in header:
			return header.index(alias)
	
	#if a streamflow column was not found...
	raise ValueError("Could not locate streamflow parameter in site data")

def empty_date_filler(prev, cur, discharge, writer):
	'''writes data between two empty dates'''
	prev = datetime.datetime.fromisoformat(prev)
	cur = datetime.datetime.fromisoformat(cur)
	days_difference = (cur - prev).days
	d=0
	while d < days_difference:
		new_date = prev + datetime.timedelta(days=d)
		new_date = new_date.isoformat()	#convert to string
		print("filled in empty day: " + new_date.split("T")[0])
		#use previous valid discharge val
		writer.writerow([new_date, discharge])
		d += 1

def discharge_record():
	'''Creates file in discharge_records folder containing datetimes and streamflow'''
	site = menu.select_site()
	if site == "Exit":
		return
	
	specific_time = get_time.get_specific_time()
	empty_date_msg = "whether to fill empty days with 0 (for EGRET compatibility)"
	empty_date_fill = menu.select_element(empty_date_msg, ["Yes", "No"])

	data = []
	i_name = ""
	
	with open("site_data/" + site, 'r') as csvfile: 
		csvreader = csv.reader(csvfile) 
		data.append(next(csvreader))
		#locate streamflow/discharge index in header
		i = streamflow_index(data[0])
		i_name = data[0][i]
		#the datetime info is in the first column
		for row in csvreader:
			#make sure there's discharge val\
			t = datetime.datetime.fromisoformat(row[0]).time()
			if row[i] != "" and get_time.equal_times(t, specific_time):
				data.append([row[0], row[i]])

	site = site.split(".")[0]   #remove type extension
	filepath = "discharge_records/" + site + "_discharge.csv"
	with open(filepath, 'w', newline="") as csvfile: 
		w = csv.writer(csvfile)
		#this file only has Datetimes and streamflows/discharges
		w.writerow(["Datetimes", i_name])
		previous_date = data[1][0]

		for d in data[1:]:
			if empty_date_fill:
				current_date = d[0]
				empty_date_filler(previous_date, current_date, d[1], w)
				previous_date = current_date
			w.writerow(d)
	print("Complete. File can be located at " + filepath)

def calculate_load(data, p):
	'''Calculates load of given parameter from data'''
	p_name = data[0][p]
	discharge_index = streamflow_index(data[0]) #need to know which column holds the discharges
	scalar = 900
	is_discharge = False
	annual_load = 0

	cur_p_val = 0

	#different parameter types are have different calculations
	concentrations = ["Nitrate plus nitrite, water, in situ, mg/L as N", "Dissolved oxygen, water, unfiltered, mg/L"]
	if p_name in concentrations:
		scalar = 900 * 28.317 * (1/1000000)
	elif p_name == "Specific conductance, water, unfiltered, microsiemens per centimeter at 25&#176;C":
		scalar = 900 * 28.317 * (1/1000000) * (1/0.6)
	elif p_name == "Streamflow, ft&#179;/s":
		is_discharge = True
	else:
		return "N/A"

	#if just calculating discharge, use val found or previously found val
	if is_discharge:
		for row in data[1:]:
			if row[p] != '':
				cur_p_val = float(row[p])
			annual_load += cur_p_val * scalar
	#for other params, keep track of previous found nondischarge val too
	else:
		cur_discharge_val = 0
		for row in data[1:]:
			if row[p] != '':
				cur_p_val = float(row[p])
			if row[discharge_index] != '':
				cur_discharge_val = float(row[discharge_index])
			annual_load += cur_p_val * cur_discharge_val * scalar
	return annual_load