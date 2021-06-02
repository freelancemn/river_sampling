import csv
import numpy
import matplotlib.pyplot as plt
from scipy.stats import skewnorm

file_name = ""
s = 10000
a = 500
m = 10
sd = 10
#d0 = numpy.random.normal(loc=m, scale=sd, size=s)
d0 = skewnorm.rvs(a, loc=m, scale=sd, size=s)
d = []
remove_negs = True

if (remove_negs):
    for e in d0:
        if e > 0:
            d.append(e)
else:
    d = d0

if (file_name == ""):
    file_name += "skew " + str(a) + "; "
    file_name += "mean " + str(m) + "; "
    file_name += "sd "   + str(sd)

plt.hist(d, density=True, bins=30)
plt.ylabel('Occurrences')
plt.xlabel('Values')
plt.title(str(a) + " skewness histogram")
plt.show()

with open("site_data/" + file_name + ".csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["datetime", "val"])
    for e in d:
        writer.writerow(["2020-08-07T03:30:00.000-06:00", e])

'''
t = sample_analysis.Model(d0, i, 1)
t.generate_maap()'''