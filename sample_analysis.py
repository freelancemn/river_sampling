import csv
import datetime
import get_time
from os import listdir
import menu
import numpy as np
import matplotlib.pyplot as plt
import random
#from scipy.stats import skewnorm
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

class Vert:
  '''A vertical line in the MAAP graph, representing the percentile values at a given sample size'''
  def __init__(self, vals, absolute_err, relative_err):
    self.vals = vals
    self.absolute_err = absolute_err
    self.relative_err = relative_err

class Model:
  '''Generates iterations amount of models from a sample space for a given parameter index'''
  def __init__(self, samples, iterations, parameter):
    self.samples = samples
    self.sample_size = 0
    self.iterations = iterations
    self.parameter = parameter
    self.verts = []
    self.potential_observations = 0
    self.actual_observations = 0
    self.model_mean = 0
    self.actual = 0     #will be a data value that holds the actual data
    self.val_ls = [[] for _ in range(len(settings.p_vals))]   #holds lines for each percentile
    self.abs_ls = [[] for _ in range(len(settings.p_vals))]
    self.rel_ls = [[] for _ in range(len(settings.p_vals))]
    self.abs_sd = [[] for _ in range(len(settings.p_vals))]
    self.rel_sd = [[] for _ in range(len(settings.p_vals))]
    self.val_m = []   #means
    self.abs_m = []
    self.rel_m = []

  def cull(self):
    '''based on the sampling strategy, remove samples from the model's potential sample space'''
    pass

  def clean(self):
    '''get rid of samples that don't have a value in the parameter index'''
    s = []
    for sample in self.samples:
      if sample[self.parameter] != "":          #if there's something in the field
        val = float(sample[self.parameter])
        s.append(val)
        #keep track of how many potential vs actual observations are being used
        self.actual_observations += 1
        self.model_mean += val
      self.potential_observations += 1
    self.samples = s
  
  def subset(self):
    '''take sample_size amounts of random samples from the culled sample space and return them as a Data object'''
    s = []
    for _ in range(self.sample_size):
      s.append(float(random.choice(self.samples)[self.parameter]))
    d = Data(s)
    return d

  def data_of_transposed_percentiles(self, matrix):
    '''return Data objects composed of the transpose of a given matrix's percentiles'''
    data_at_p = []
    for p in range(len(settings.p_vals)):
      pv = []         #percentile values
      for d in matrix:
        pv.append(d.percentiles[p])
      data_at_p.append(Data(pv, calc_sd=True, calc_perc=False))
    return data_at_p

  def mean_of_data_matrix(self, matrix):
    '''return the mean of a matrix of data using the means in the data'''
    means = []
    for d in matrix:
      means.append(d.mean)
    return np.mean(means)

  def iterate(self, actual):
    '''calculate abs and rel diffs between rand subset of culled samples and original dataset, iterations times, for given sample size'''
    absolute_diffs = []
    relative_diffs = []
    model_vals = []

    for _ in range(self.iterations):
      sub = self.subset()
      model_vals.append(sub)
      absolute_diffs.append(Data([a - m for a, m in zip(actual.percentiles, sub.percentiles)])) #diffs between subset percentiles and actual percentiles
      relative_diffs.append(Data([100/a * (a - m) for a, m in zip(actual.percentiles, sub.percentiles)]))

    self.val_m = self.mean_of_data_matrix(model_vals)
    self.abs_m = self.mean_of_data_matrix(absolute_diffs)
    self.rel_m = self.mean_of_data_matrix(relative_diffs)

    #generate Data objects for each percentile of the abs and rel diffs
    self.verts.append(Vert(self.data_of_transposed_percentiles(model_vals), self.data_of_transposed_percentiles(absolute_diffs), self.data_of_transposed_percentiles(relative_diffs)))

  def generate_maap(self):
    '''run the iterate function for each sample size in settings.py'''
    #generate Data from the original set of samples'''
    original = self.samples
    self.clean()
    self.actual = Data(self.samples, calc_sd=True)

    #prepare the culled sample space, record how many samples were lost during culling
    self.samples = original
    num_culled = len(self.samples)
    self.cull()
    num_culled -= len(self.samples)
    #self.clean()

    #commence the iterating
    for sn in settings.sample_sizes:
      self.sample_size = sn
      self.iterate(self.actual)

    #generate "lines" from the verts for each percentile
    for v in self.verts:
      for p in range(len(settings.p_vals)):
          self.val_ls[p].append(round(v.vals[p].mean, 4))
          self.abs_ls[p].append(round(v.absolute_err[p].mean, 4))
          self.rel_ls[p].append(round(v.relative_err[p].mean, 4))
          self.abs_sd[p].append(round(v.absolute_err[p].sd, 4))
          self.rel_sd[p].append(round(v.relative_err[p].sd, 4))

    for l in range(len(self.val_ls)):
      plt.errorbar(settings.sample_sizes, self.val_ls[l], yerr=self.abs_ls[l])

    plt.suptitle("hello!")
    plt.show()

    #head = ["subsamples", num_culled, self.actual.mean]
    #return head + flatten(val_ls) + flatten(abs_ls) + flatten(rel_ls)

def data_in_time_range(file_location, time_range):
  '''returns data from file that is restrained to a time_range'''
  with open(file_location, 'r') as csvfile: 
    csvreader = csv.reader(csvfile) 
    data = []
    data.append(next(csvreader))

    #the datetime info is in the first column
    for row in csvreader: 
      dt = datetime.datetime.fromisoformat(row[0])
      if dt > time_range[1]:    #only use data within the timerange
        break
      elif dt < time_range[1]:
        data.append(row)
  
    return data 

def transpose(m):
  '''returns transpose of 2d list'''
  return [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]

def analyze(iterations=0, time_range=0):
  '''run the generate_maap function for each parameter in a site's data'''
  
  #allow the user to select the site, number of iterations, and time_range
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

  #write all of the maap data to the summary.csv file
  with open("model_summaries.csv", "a", newline='') as csvfile:
    writer = csv.writer(csvfile) 

    for p in range(1, len(data[0])):
      m = Model(data[1:], iterations, p)
      m.generate_maap() 

      dt_info = [time_range[0].date(), time_range[0].time(), time_range[1].date(), time_range[1].time()]#, (time_range[1].date()-time_range[0].date()).days]
      head = [p, site.split(".")[0], data[0][p]] + dt_info

      val_ls_t = transpose(m.val_ls)
      abs_ls_t = transpose(m.abs_ls)
      rel_ls_t = transpose(m.rel_ls)
      abs_sd_t = transpose(m.abs_sd)
      rel_sd_t = transpose(m.rel_sd)
      
      for s in range(len(settings.sample_sizes)):
        head_e = head + ["INSERT SAMPLING STRATEGY", iterations, settings.sample_sizes[s], "perc culled", np.mean(m.val_m), np.std(m.val_m)]
        writer.writerow(head_e + val_ls_t[s] + [np.mean(m.abs_m), np.std(m.abs_m)] + abs_ls_t[s] + [np.mean(m.rel_m), np.std(m.rel_m)] + rel_ls_t[s] + abs_sd_t[s] + rel_sd_t[s])

      with open("site_summaries.csv", "a", newline='') as f:
        w = csv.writer(f)

        observation_section = [m.potential_observations, m.actual_observations, m.potential_observations - m.actual_observations]
        print(observation_section)
        r = head + observation_section + ["USGS", m.actual.mean] + list(m.actual.percentiles) + [m.actual.sd]
        w.writerow(r)

      del m