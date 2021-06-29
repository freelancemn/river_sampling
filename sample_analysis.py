import abbreviations
import csv
import data_tools
import load_calculator
import model
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import settings

def analyze(analysis_params = 0):
  '''run the generate_maap function for each parameter in a site's data'''
  if not analysis_params:
    analysis_params = data_tools.Analysis_Params()
  
  site = analysis_params.site
  iterations = analysis_params.iterations
  time_range = analysis_params.time_range

  data = data_tools.data_in_time_range("site_data/"+site, time_range)

  #write all of the maap data to the summary.csv file
  with open("summaries/model_summaries.csv", "a", newline='') as csvfile:
    writer = csv.writer(csvfile) 

    for p in range(1, len(data[0])):
      p_name = abbreviations.shorten(data[0][p])
      print("Analyzing " + p_name)
      annual_load = load_calculator.calculate_load(data, p)
      
      m = model.Model(data[1:], iterations, p)
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