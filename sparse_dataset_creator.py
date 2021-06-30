import csv
import data_tools
import random
import get_time
import menu
from operator import itemgetter

class Sparse_Params:
  def __init__(self):
    self.site = menu.select_site("superset")
    self.dt = get_time.select_datetime("start year", just_year=True)
    self.num_yrs = menu.select_integer("number of years")
    self.samples_per_yr = menu.select_integer("number of samples per year")
    headers = data_tools.data_in_time_range("site_data/" + self.site, just_headers=True)
    self.p_index = menu.select_element("parameter", headers[1:], return_index=True)
    self.p_name = headers[self.p_index]

def date_from_datetime_str(dt):
  '''returns date string from datetime string'''
  return dt.split("T")[0]

def remove_date(samples, date):
  '''removes all samples that fall on a specified day'''
  new_samples = []
  for s in samples:
    #check the date portion of the sample
    if date_from_datetime_str(s[0]) != date:
      new_samples.append(s)
  return new_samples

def fill_year(sp, years):
  '''get specified num samples from year, or max if less than samples_per_yr'''
  yearly_data = data_tools.data_in_time_range("site_data/" + sp.site, years)
  samples = []
  while (len(samples) < sp.samples_per_yr):
    if len(yearly_data) == 1:   #if only the header is left
      print("Not enough valid samples in year " + str(years[0].year))
      print("Will use " + str(len(samples)) + " samples for this year")
      break
    s = random.choice(yearly_data[1:])
    if s[sp.p_index] == '':     #if param of interest is empty, remove sample
      yearly_data.remove(s)
    else:
      date = date_from_datetime_str(s[0])
      yearly_data = remove_date(yearly_data, date)
      samples.append([date, s[sp.p_index]])
  return samples

def make_sparse_dataset():
  '''User defines site/range/samples_per_yr, random subset, one sample per day'''
  all_samples = []

  sp = Sparse_Params()

  for y in range(0, sp.num_yrs):
    years = [sp.dt.replace(year = sp.dt.year + y), sp.dt.replace(year = sp.dt.year + y + 1)]
    print("Collecting samples from " + str(years[0].year))
    
    samples = fill_year(sp, years)
    all_samples.extend(sorted(samples, key=itemgetter(0)))

  file_name = sp.site.split(".")[0] + " " + str(sp.dt).split("-")[0] + " " + str(sp.num_yrs)
  file_name += " " + str(sp.samples_per_yr) + " " + str(sp.p_index) + "_sparse.csv"
  file_path = "sparse_datasets/" + file_name

  with open(file_path, "w", newline='') as f:
    w = csv.writer(f)
    w.writerow(["Date", sp.p_name])
    for s in all_samples:
      w.writerow(s)
  print("Complete. File can be located at " + file_path)