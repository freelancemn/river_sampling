import csv
import sample_analysis
import random
import get_time
import menu
from operator import itemgetter

#run this function to specify/generate sparse_dataset.csv

'''def date_is_unique(samples, date):
    for s in samples:
        if date == s[0]:
            return False
    return True'''

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

def make_sparse_dataset():
    '''User defines site/range/samples_per_yr, random subset, one sample per day'''
    all_samples = []
    site = menu.select_site("superset")
    dt = get_time.select_datetime("start year", just_year=True)
    num_yrs = menu.select_integer("number of years")
    samples_per_yr = menu.select_integer("number of samples per year")
    p_index = menu.select_integer("parameter index (col number w/ datetime being col 0)")
    header = ""

    for y in range(0, num_yrs):
        years = [dt.replace(year = dt.year + y), dt.replace(year = dt.year + y + 1)]
        yearly_data = sample_analysis.data_in_time_range("site_data/" + site, years)
        header = yearly_data[0][p_index]
        samples = []
        print("Collecting samples from " + str(years[0].year))

        while (len(samples) < samples_per_yr):
            if len(yearly_data) == 1:   #if only the header is left
                print("Not enough valid samples in year " + str(years[0].year))
                print("Will use " + str(len(samples)) + " samples for this year")
                break
            s = random.choice(yearly_data[1:])
            if s[p_index] == '':            #if param of interest is empty, remove sample
                yearly_data.remove(s)
            else:
                date = date_from_datetime_str(s[0])
                yearly_data = remove_date(yearly_data, date)
                samples.append([date, s[p_index]])
        
        all_samples.extend(sorted(samples, key=itemgetter(0)))

    file_name = site.split(".")[0] + " " + str(dt).split("-")[0] + " " + str(num_yrs)
    file_name += " " + str(samples_per_yr) + " " + str(p_index) + ".csv"

    with open("sparse_datasets/" + file_name, "w", newline='') as f:
        w = csv.writer(f)
        w.writerow(["Date", header])
        for s in all_samples:
            w.writerow(s)