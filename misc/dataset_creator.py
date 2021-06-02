import csv
import sample_analysis
import random
import get_time
from operator import itemgetter

all_samples = []
dt = get_time.select_datetime("start year")
for y in range(0, 5):
    years = [dt.replace(year = dt.year + y), dt.replace(year = dt.year + y + 1)]
    yearly_data = sample_analysis.data_in_time_range("dataset_chunk.csv", years)
    samples = []
    while (len(samples) < 50):
        s = random.choice(yearly_data)
        if s[-1] != '':
            samples.append([s[0], s[-1]])
    all_samples.extend(sorted(samples, key=itemgetter(0)))

header = ["DateTimes", "Nitrate plus nitrite, water, in situ, mg/L as N"]

with open("sparse_dataset.csv", "a", newline='') as f:
    w = csv.writer(f)
    w.writerow(header)
    for s in all_samples:
        w.writerow(s)