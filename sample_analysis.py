import csv
import datetime
import get_time
from os import listdir
import menu
import numpy as np
import matplotlib.pyplot as plt
import random
import settings

class Data:
  def __init__(self, values, calc_sd = False, calc_perc = True, calc_mean = True):
    self.mean = 0
    self.percentiles = []
    self.sd = 0

    if calc_sd == True:
      self.sd = np.std(values)
    if calc_mean == True:
      self.mean = sum(values)/len(values)
    if calc_perc == True:
      self.percentiles = np.percentile(values, settings.p_vals)

class Line:
  def __init__(self, absolute_err, relative_err):
    #self.model = model
    self.absolute_err = absolute_err
    self.relative_err = relative_err

class Model:
  def __init__(self, samples, iterations, parameter):
    self.samples = samples
    self.sample_size = 0
    self.iterations = iterations
    self.parameter = parameter  #make this a list
    self.lines = []
    self.potential_observations = 0
    self.actual_observations = 0
    self.model_mean = 0

  def cull(self):
    pass

  def cull_missing(self):
    #generate the actual values before doing this 
    #get rid of the lines that have missing data for the parameters we're observing
    #allow user to set threshold % of how much missing is acceptable
    pass

  def clean(self):
    s = []
    for sample in self.samples:
      if sample[self.parameter] != "":
        val = float(sample[self.parameter])
        s.append(val)
        self.actual_observations += 1
        self.model_mean += val
      self.potential_observations += 1
    self.samples = s
  
  def subset(self):
    s = []
    for _ in range(self.sample_size):
      s.append(random.choice(self.samples))
    return Data(s)

  def data_of_matrix(self, matrix):
    data_at_p = []
    for p in range(len(settings.p_vals)):
      pv = []
      for d in matrix:
        pv.append(d.percentiles[p])
      data_at_p.append(Data(pv, calc_sd=True, calc_perc=False))
    return data_at_p

  def iterate(self, actual):
    #model = []
    absolute_diffs = []
    relative_diffs = []

    for _ in range(self.iterations):
      sub = self.subset()
      #model.append(sub)
      absolute_diffs.append(Data([a - m for a, m in zip(actual.percentiles, sub.percentiles)]))
      relative_diffs.append(Data([100/a * (a - m) for a, m in zip(actual.percentiles, sub.percentiles)]))

    #self.lines.append(Line(self.data_of_matrix(model), self.data_of_matrix(absolute_diffs), self.data_of_matrix(relative_diffs)))
    self.lines.append(Line(self.data_of_matrix(absolute_diffs), self.data_of_matrix(relative_diffs)))

  def generate_maap(self):
    #change this so it looks at the list of parameters
    original = self.samples
    self.clean()
    actual = Data(self.samples, calc_sd=True)

    self.samples = original
    num_culled = len(self.samples)
    self.cull()
    num_culled -= len(self.samples)
    self.clean()

    for sn in settings.sample_sizes:
      self.sample_size = sn
      self.iterate(actual)
      
    #try to put things into a table format before generating the graph
    line_ls = [[] for _ in range(len(settings.p_vals))]
    abs_ls = [[] for _ in range(len(settings.p_vals))]
    rel_ls = [[] for _ in range(len(settings.p_vals))]

    for l in self.lines:
      for p in range(len(settings.p_vals)):
          line_ls[p].append(l.absolute_err[p].mean)
          abs_ls[p].append(l.absolute_err[p].sd)
          rel_ls[p].append(l.relative_err[p].sd)

    '''for l in range(len(line_ls))[::3]:
      plt.errorbar(settings.sample_sizes, line_ls[l], yerr=abs_ls[l])

    plt.show()'''

    head = [self.potential_observations, self.actual_observations, actual.mean, self.model_mean/self.actual_observations, num_culled]
    return head + line_ls + abs_ls + rel_ls

def data_in_time_range(file_location, time_range):
  with open(file_location, 'r') as csvfile: 
    csvreader = csv.reader(csvfile) 
    data = []
    data += next(csvreader)

    for row in csvreader: 
      dt = datetime.datetime.fromisoformat(row[0])
      if dt > time_range[0]:
        break
      elif dt < time_range[1]:
        data += row
  
    return data 

def analyze(site, iterations=0, time_range=0):
  site = menu.select_element("site", listdir("site_data") + ["Exit"])
  if site == "Exit":
    return
    
  if iterations == 0:
    iterations = menu.select_integer("Number of iterations")
  if time_range == 0:
    start_datetime = get_time.select_datetime("Selecting start date/time")
    end_datetime = get_time.select_datetime("Selecting end date/time")
    
    while end_datetime < start_datetime:
      print("Select an end date/time that's greater than " + str(start_datetime))
      end_datetime = get_time.select_datetime("Selecting end date/time")
    time_range = [start_datetime, end_datetime]

  data = data_in_time_range("site_data/"+site, time_range)

  with open("summary.csv", "a") as csvfile:
    writer = csv.writer(csvfile) 

    for p in range(1, len(data[0])):
      m = Model(data[1:], iterations, p)
      d = m.generate_maap()
      del m

      dt_info = [time_range[0].date(), time_range[0].time(), time_range[1].date(), time_range[1].time(), (time_range[1].date()-time_range[0].date()).days]
      head = [p, site.split(".")[0], data[0][p]] + dt_info + ["INSERT SAMPLING STRATEGY", iterations]

      writer.writerow(head + d)

#   REFER TO PAUL'S EMAIL