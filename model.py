import data_tools
import numpy as np
import random
import settings

class Vert:
  '''Vertical line in the MAAP graph, representing percentile values at a given sample size'''
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

    if self.samples == []:
      print("No samples left after culling")
      return 1

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

    return 0