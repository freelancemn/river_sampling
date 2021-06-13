import csv
from os import listdir
import sample_analysis
import random
import get_time
import menu
from operator import itemgetter

#run this function to specify/generate sparse_dataset.csv

def date_is_unique(samples, date):
    for s in samples:
        if date == s[0]:
            return False
    return True


all_samples = []
site = menu.select_element("site", listdir("site_data") + ["Exit"])
dt = get_time.select_datetime("start year")
num_yrs = menu.select_integer("number of years")
samples_per_yr = menu.select_integer("number of samples per year")
p_index = menu.select_integer("parameter index (col number w/ datetime being col 0)")
header = ""

for y in range(0, num_yrs):
    years = [dt.replace(year = dt.year + y), dt.replace(year = dt.year + y + 1)]
    yearly_data = sample_analysis.data_in_time_range("site_data/" + site, years)
    header = yearly_data[0][p_index]
    samples = []
    while (len(samples) < samples_per_yr):
        s = random.choice(yearly_data)
        date = s[0].split("T")[0]
        if s[p_index] != '' and date_is_unique(samples, date):
            samples.append([date, s[p_index]])
    all_samples.extend(sorted(samples, key=itemgetter(0)))

file_name = site.split(".")[0] + " " + str(dt).split("-")[0] + " " + str(num_yrs)
file_name += " " + str(samples_per_yr) + " " + str(p_index) + ".csv"

with open("sparse_datasets/" + file_name, "w", newline='') as f:
    w = csv.writer(f)
    w.writerow(["Date", header])
    for s in all_samples:
        w.writerow(s)