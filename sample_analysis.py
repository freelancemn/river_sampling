import abbreviations
import csv
import data_tools
import load_calculator
import model
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import settings

def analyze():
  '''generate maap graph for site(s)'''
  analyze_setup()

def write_analysis(p, ap, site, data, m):
  '''write data to the summaries files'''
  annual_load = load_calculator.calculate_load(data, p)
  dt_info = [ap.time_range[0].date(), ap.time_range[0].time(), ap.time_range[1].date(), ap.time_range[1].time()]
  head = [p, site.split(".")[0], data[0][p]] + dt_info

  val_ls_t = data_tools.transpose(m.val_ls)
  abs_ls_t = data_tools.transpose(m.abs_ls)
  rel_ls_t = data_tools.transpose(m.rel_ls)
  abs_sd_t = data_tools.transpose(m.abs_sd)
  rel_sd_t = data_tools.transpose(m.rel_sd)
  
  #write all of the maap data to the summary.csv file
  with open("summaries/model_summaries.csv", "a", newline='') as csvfile:
    writer = csv.writer(csvfile) 
    for s in range(len(settings.sample_sizes)):
      head_e = head + ["INSERT SAMPLING STRATEGY", ap.iterations, settings.sample_sizes[s], "perc culled", np.mean(m.val_m), np.std(m.val_m)]
      writer.writerow(head_e + val_ls_t[s] + [np.mean(m.abs_m), np.std(m.abs_m)] + abs_ls_t[s] + [np.mean(m.rel_m), np.std(m.rel_m)] + rel_ls_t[s] + abs_sd_t[s] + rel_sd_t[s])

  with open("summaries/site_summaries.csv", "a", newline='') as f:
    w = csv.writer(f)

    observation_section = [m.potential_observations, m.actual_observations, m.potential_observations - m.actual_observations]
    r = head + observation_section + ["USGS", m.actual.mean] + list(m.actual.percentiles) + [m.actual.sd] + [annual_load]
    w.writerow(r)

def calculate_analysis(p, ap, site, data):
  p_name = abbreviations.shorten(data[0][p])
  print("Analyzing " + p_name)
  
  m = model.Model(data[1:], ap.iterations, p)
  empty_check = m.generate_maap()

  if empty_check == True:
    print ("No samples were found in this timerange for", data[0][p])
  else:
    site_name = ''.join(site.split(".")[:-1])    #remove .csv text
    path_1 = 'maap_graphs/' + site_name + '/' 
    
    title = str(ap.time_range[0]) + " through " + str(ap.time_range[1])
    title += " " + str(ap.iterations) + " iterations"
    path_2 = '/' + title.replace(":", " ").replace(".", "d") + '/'
    
    save_dest = path_1 + p_name + path_2
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

    write_analysis(p, ap, site, data, m)

    del m

def analyze_setup(analysis_params = 0):
  '''run the generate_maap function for each parameter in a site's data'''
  ap = analysis_params  #define shorthand
  choose_site_params = True
  if not ap:
    ap = data_tools.Analysis_Params()

  for site in ap.site:
    data = data_tools.data_in_time_range("site_data/"+site, ap.time_range)

    if choose_site_params:
      site_params = ap.choose_site_params(data[0])
      choose_site_params = False

    for p in range(len(site_params)):
      if site_params[p] == True:
        calculate_analysis(p+1, ap, site, data)  #account for datetime column