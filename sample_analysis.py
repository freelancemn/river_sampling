import abbreviations
import csv
import data_tools
import get_time
import load_calculator
import menu
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import random
import settings

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
      s.append(random.choice(self.samples))
    d = data_tools.Data(s)
    return d

  def data_of_transposed_percentiles(self, matrix):
    '''return Data objects composed of the transpose of a given matrix's percentiles'''
    data_at_p = []
    for p in range(len(settings.p_vals)):
      pv = []         #percentile values
      for d in matrix:
        pv.append(d.percentiles[p])
      data_at_p.append(data_tools.Data(pv, calc_sd=True, calc_perc=False))
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
      absolute_diffs.append(data_tools.Data([a - m for a, m in zip(actual.percentiles, sub.percentiles)])) #diffs between subset percentiles and actual percentiles
      relative_diffs.append(data_tools.Data([100/a * (a - m) for a, m in zip(actual.percentiles, sub.percentiles)]))

    self.val_m = self.mean_of_data_matrix(model_vals)
    self.abs_m = self.mean_of_data_matrix(absolute_diffs)
    self.rel_m = self.mean_of_data_matrix(relative_diffs)

    #generate Data objects for each percentile of the abs and rel diffs
    self.verts.append(Vert(self.data_of_transposed_percentiles(model_vals), self.data_of_transposed_percentiles(absolute_diffs), self.data_of_transposed_percentiles(relative_diffs)))

  def generate_maap(self):
    '''run the iterate function for each sample size in settings.py. Returns 1 if no samples in range for param, 0 if success'''
    #generate Data from the original set of samples'''
    original = self.samples
    self.clean()

    if self.samples == []:
      return 1
    self.actual = data_tools.Data(self.samples, calc_sd=True)

    #prepare the culled sample space, record how many samples were lost during culling
    self.samples = original
    num_culled = len(self.samples)
    self.cull()
    num_culled -= len(self.samples)
    self.clean()

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

    #head = ["subsamples", num_culled, self.actual.mean]
    #return head + flatten(val_ls) + flatten(abs_ls) + flatten(rel_ls)
    return 0

def analyze(iterations=0, time_range=0):
  '''run the generate_maap function for each parameter in a site's data'''
  
  #allow the user to select the site, number of iterations, and time_range
  site = menu.select_site()
  if site == "Exit":
    return
    
  if iterations == 0:
    iterations = menu.select_integer("Number of iterations")
  if time_range == 0:
    time_range = get_time.select_timerange()

  data = data_tools.data_in_time_range("site_data/"+site, time_range)

  #write all of the maap data to the summary.csv file
  with open("summaries/model_summaries.csv", "a", newline='') as csvfile:
    writer = csv.writer(csvfile) 

    for p in range(1, len(data[0])):
      p_name = abbreviations.shorten(data[0][p])
      print("Analyzing " + p_name)
      annual_load = load_calculator.calculate_load(data, p)
      #p = len(data[0]) - 1  #just checks final param, delete this later
      
      m = Model(data[1:], iterations, p)
      empty_check = m.generate_maap()

      if empty_check == True:
        print ("No samples were found in this timerange for", data[0][p])
      else:
        site_name = ''.join(site.split(".")[:-1])    #remove .csv text
        path_1 = 'maap_graphs/' + site_name + '/' 
        
        title = str(time_range[0]) + " through " + str(time_range[1])
        title += " " + str(iterations) + " iterations"
        path_2 = '/' + title.replace(":", " ").replace(".", "d") + '/'
        
        save_dest = path_1 + p_name + path_2
        '''try:
          Path(save_dest).mkdir(parents=True, exist_ok=True)
        except:     #strange filenotfounderror from pathlib for some parameters
          save_dest = path_1 + p_name.split(",")[0] + path_2
          Path(save_dest).mkdir(parents=True, exist_ok=True)'''
        Path(save_dest).mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(10,6))
        for l in range(len(m.val_ls)):   #absolute error bars graph
          plt.errorbar(settings.sample_sizes, m.val_ls[l], yerr=m.abs_ls[l], label=str(settings.p_vals[l]))
        plt.xlabel("Sample size")
        plt.ylabel(p_name + ", absolute error bars")
        plt.suptitle(title)
        plt.legend(title='Percentiles', bbox_to_anchor=(1, 1), loc='upper left')
        plt.savefig(save_dest + 'abs.png')
        plt.close()

        plt.figure(figsize=(10,6))
        for l in range(len(m.val_ls)):   #relative error bars graph
          plt.errorbar(settings.sample_sizes, m.val_ls[l], yerr=m.rel_ls[l], label=str(settings.p_vals[l]))
        plt.xlabel("Sample size")
        plt.ylabel(p_name + ", relative error bars")
        plt.suptitle(title)
        plt.legend(loc="upper right")
        plt.legend(title='Percentiles', bbox_to_anchor=(1, 1), loc='upper left')
        plt.savefig(save_dest + 'rel.png')
        plt.close()

        dt_info = [time_range[0].date(), time_range[0].time(), time_range[1].date(), time_range[1].time()]#, (time_range[1].date()-time_range[0].date()).days]
        head = [p, site.split(".")[0], data[0][p]] + dt_info

        val_ls_t = data_tools.transpose(m.val_ls)
        abs_ls_t = data_tools.transpose(m.abs_ls)
        rel_ls_t = data_tools.transpose(m.rel_ls)
        abs_sd_t = data_tools.transpose(m.abs_sd)
        rel_sd_t = data_tools.transpose(m.rel_sd)
        
        for s in range(len(settings.sample_sizes)):
          head_e = head + ["INSERT SAMPLING STRATEGY", iterations, settings.sample_sizes[s], "perc culled", np.mean(m.val_m), np.std(m.val_m)]
          writer.writerow(head_e + val_ls_t[s] + [np.mean(m.abs_m), np.std(m.abs_m)] + abs_ls_t[s] + [np.mean(m.rel_m), np.std(m.rel_m)] + rel_ls_t[s] + abs_sd_t[s] + rel_sd_t[s])

        with open("summaries/site_summaries.csv", "a", newline='') as f:
          w = csv.writer(f)

          observation_section = [m.potential_observations, m.actual_observations, m.potential_observations - m.actual_observations]
          r = head + observation_section + ["USGS", m.actual.mean] + list(m.actual.percentiles) + [m.actual.sd] + [annual_load]
          w.writerow(r)

        del m