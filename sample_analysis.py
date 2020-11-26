import csv
import datetime
import get_time
from os import listdir
import menu
import numpy as np
import matplotlib.pyplot as plt
import random
import settings
import table_math

def populate_model(site_id, model_possibilities, samples, iterations, actual):
  model_location = "site_tables/" + str(site_id).split('.')[0] + "/model.csv"
  percentile_location = "site_tables/" + str(site_id).split('.')[0] + "/percentiles.csv"

  #Go through each year of site's history write, data to file
  with open(model_location, "w+", newline='') as modelfile:
    model_writer = csv.writer(modelfile, delimiter=',')
    with open(percentile_location, "w+", newline='') as percentilefile:
      percentile_writer = csv.writer(percentilefile, delimiter=",")
      percentile_writer.writerow([x * settings.grain for x in range(1, int(100/settings.grain))] + ["avg"]) #write header row of percentile nums
      for _ in range(iterations):
        model_set = []
        for _ in range(samples):
          model_set.append(random.choice(model_possibilities))
        model_writer.writerow(model_set)
        p = percentiles(model_set, settings.grain)
        percentile_writer.writerow(p + [np.average(p)])
  
  return (table_math.table_averages(percentile_location, iterations), table_math.table_sd(percentile_location, actual))

def percentiles(set, grain):
  '''Finds the percentiles for a set'''
  p = []
  for x in range(1, int(100/grain)):
    p.append(np.percentile(set, x*grain))
  return p

def flow_percentile(file_location, start_datetime, end_datetime, grain, percentile):
  with open(file_location, "r") as csvfile:
    flow_rates = []
    flow_column = 0
    is_header = True
    csv_reader = csv.reader(csvfile, delimiter=',')
    flow_column = 0
    for row in csv_reader:
      #print(row)
      if is_header:
        flow_column = row.index("Streamflow, ft&#179;/s")
        is_header = False
      else:
        dt = datetime.datetime.fromisoformat(row[0])
        if dt >= start_datetime and row[flow_column] != '':
          flow_rates.append(float(row[flow_column]))
        if dt >= end_datetime:
          break
  return (flow_column, percentiles(flow_rates, grain)[percentile])

def collect_samples(set_sample_size = True, delim = ","):
  '''Conduct sampling analysis'''
  site = menu.select_element("site", listdir("site_data"))
  file_location = "site_data/" + site

  with open(file_location, "r") as csvfile:
    site_id = file_location.split("/")[1]
    csv_reader = csv.reader(csvfile, delimiter = delim)
    line_count = 0
    sample_count = 0
    potential_count = 0
    variable = 0
    v_name = ""

    start_datetime = get_time.select_datetime("Selecting start date/time")
    end_datetime = get_time.select_datetime("Selecting end date/time")
    while end_datetime < start_datetime:
      print("Select an end date/time that's greater than " + str(start_datetime))

    strategies = ["weekdays and times", "flow rate"]
    strategy_type = menu.select_element("strategy", strategies)
    flow_p = 0
    flow_column = 0
    below_flow = 0
    low_flow = 25
    if strategy_type == "flow rate":
      f = flow_percentile(file_location, start_datetime, end_datetime, low_flow, 0)
      flow_column = f[0]
      flow_p = f[1]
      #print(flow_p)
      
    weekdays = []
    time_range = []
    samples = 0
    iterations = 0
    actual_set = []
    model_possibilities = []

    for row in csv_reader:
      if line_count == 0: #Select parameters using header info
        print('here"s a row', row)
        variable = menu.select_element("variable", row[1:], True)
        v_name = row[variable]
        if strategy_type == "weekdays and times":
          weekdays = get_time.range_week()
          time_range = get_time.range_time()
        if set_sample_size:
          samples = menu.select_integer("number of samples")
        iterations = menu.select_integer("number of iterations")
      else:
        dt = datetime.datetime.fromisoformat(row[0])
        if dt > end_datetime:
          break
        if dt >= start_datetime:
          potential_count += 1
          if row[variable] != '':
            sample_count += 1
            #Populate actual sampleset
            val = float(row[variable])
            actual_set.append(val)
            #Add time to distribution model if it meets requirements
            if strategy_type == "weekdays and times" and get_time.in_range(dt, weekdays, time_range):
              model_possibilities.append(val)
            elif strategy_type == "flow rate" and row[flow_column] !='':
              if float(row[flow_column]) < flow_p:
                model_possibilities.append(val)
                below_flow += 1
      line_count += 1
    
    actual_percentiles = percentiles(actual_set, settings.grain)
    actual_percentiles += [np.average(actual_percentiles)]
    model_stats = populate_model(site_id, model_possibilities, samples, iterations, actual_percentiles)
    print("absolute SD\n", model_stats[1][0])
    print("percent SD\n", model_stats[1][1])

    strategy_code = 0
    if strategy_type == "weekdays and times":
      strategy_code = get_time.codify(weekdays, time_range)
    elif strategy_type == "flow rate":
      strategy_code = str(int(below_flow/sample_count)) + str(low_flow)
    
    actual_mean = sum(actual_set)/len(actual_set)
    model_mean = sum(model_possibilities)/len(model_possibilities)

    print(samples, "samples")
    print([a - b for a, b in zip(actual_percentiles, model_stats[0])])

    #write_site_sheet(site_id, v_name, start_datetime, end_datetime, strategy_code, iterations, samples, potential_count, sample_count, actual_mean, model_mean, actual_percentiles[:-1], model_stats[0][:-1])

    #return calculate_error(v_name, actual_percentiles, model_array)

def write_site_sheet(site_id, v_name, start_datetime, end_datetime, sampling_strategy, iterations, samples, potential_obs, actual_obs, actual_mean, model_mean, actual_percentiles, model_percentiles):
  #model_run_count = 1
  file_location = "site_tables/" + str(site_id).split('.')[0] + "/analysis.csv"
  sample_x = [5]
  plt_actual = [actual_percentiles[0]]
  plt_model = [model_percentiles[0]]
  #Go through each year of site's history write, data to file
  with open(file_location, "a") as myfile:
    writer = csv.writer(myfile, delimiter=',')
    new_row = [v_name, start_datetime.date().strftime("%m/%d/%Y"), start_datetime.time().strftime("%H:%M"), end_datetime.date().strftime("%m/%d/%Y"), end_datetime.time().strftime("%H:%M"), sampling_strategy, iterations, samples, (end_datetime - start_datetime).days, potential_obs, actual_obs, actual_mean, model_mean]

    #print(actual_percentiles)

    interlaced_means = []
    interlaced_means.append(actual_percentiles[0])
    interlaced_means.append(model_percentiles[0])
    for i in range(1, len(actual_percentiles), 2):
      interlaced_means.append(actual_percentiles[i])
      interlaced_means.append(model_percentiles[i])
      plt_actual.append(actual_percentiles[i])
      plt_model.append(model_percentiles[i])
      sample_x += [5 * (i+1)]
    interlaced_means.append(actual_percentiles[-1])
    interlaced_means.append(model_percentiles[-1])
    new_row += interlaced_means
    #print(new_row)
    writer.writerow(new_row)

  sample_x += [95]
  plt_actual += [actual_percentiles[-1]]
  plt_model += [model_percentiles[-1]]
  print (sample_x)
  plt.errorbar(sample_x, plt_actual, yerr=[abs(a-b) for a, b in zip(plt_model, plt_actual)], label="Actual")
  plt.plot(sample_x, plt_model, label="Model")
  plt.legend(loc="upper right")
  
  # naming the x axis 
  plt.xlabel("Percentiles (%)") 
  # naming the y axis 
  plt.ylabel(v_name) 
  
  # giving a title to my graph 
  plt.title('Actual VS Model for ' + str((end_datetime - start_datetime).days) + " days, " + str(samples)  + " samples, " + str(iterations) + " iterations. Strategy code " + sampling_strategy) 

  # function to show the plot 
  plt.show()

def calculate_error(v_name, actual_p, model_a):
  '''for m in range(len(model_a)):
    differences = []
    for p in range(len(actual_p)):
      differences.append(actual_p[p] - model_a[m][p])
    # plotting the points
    plt.plot(settings.sample_sizes, differences)'''

  for m in range(len(model_a)):
    differences = []
    for p in range(len(model_a[m])):
      differences.append(actual_p[m] - model_a[m][p])
      #print(actual_p[p], model_a[p][m])
    # plotting the points
    print(differences)
    plt.plot(settings.sample_sizes, differences, label=p+1)
  
  plt.legend(loc="upper right")
  
  # naming the x axis 
  plt.xlabel('Samples') 
  # naming the y axis 
  plt.ylabel('Difference') 
  
  # giving a title to my graph 
  plt.title('actual VS Model for ' + v_name) 

  # function to show the plot 
  plt.show() 