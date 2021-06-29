import csv
import datetime
import get_time
import menu
import numpy as np
import settings

def flatten(l):
  '''Turn a 2d list into a 1d list'''
  flat_list = [item for sublist in l for item in sublist]
  return flat_list

class Data:
  '''Associates a list of nums with their SD, mean, and percentiles'''
  def __init__(self, values, calc_sd = False, calc_perc = True, calc_mean = True):
    self.mean = 0
    self.percentiles = []
    self.sd = 0

    #Each calculation is optional to save on computation time
    if calc_sd == True:
      self.sd = np.std(values)
    if calc_mean == True:
      self.mean = sum(values)/len(values)
    if calc_perc == True:
      self.percentiles = np.percentile(values, settings.p_vals)

def data_in_time_range(file_location, time_range):
  '''returns data from file that is restrained to a time_range'''
  with open(file_location, 'r') as csvfile: 
    csvreader = csv.reader(csvfile) 
    data = []
    data.append(next(csvreader))

    #the datetime info is in the first column
    for row in csvreader: 
      dt = datetime.datetime.fromisoformat(row[0])
      if dt < time_range[1] and dt > time_range[0]:    #only use data within the timerange
        data.append(row)
  
    return data 

def transpose(m):
  '''returns transpose of 2d list'''
  return [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]

class Analysis_Params():
  '''set of parameters for running sample_analysis'''
  def __init__(self):
    #select a site
    self.site = menu.select_site()
    if self.site == "Exit":
      raise ValueError('Exit chosen. Stopping sample analysis')
      
    #select num of iterations and time range
    self.iterations = menu.select_integer("Number of iterations")
    self.time_range = get_time.select_timerange()