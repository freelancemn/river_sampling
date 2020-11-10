import csv
import numpy as np

def table_averages(file, total_lines):
    with open(file, "r") as myfile:
        csv_reader = csv.reader(myfile, delimiter=',')
        line_count = 0
        running_average = []
        for line in csv_reader:
            if line_count == 0:
                running_average = [0.0] * len(line)
            else:
                running_average = [a + float(b)/total_lines for a, b in zip(running_average, line)]
            line_count += 1
            if line_count > total_lines:
                break
        return running_average

def table_sd(file, actual):
    with open(file, "r") as myfile:
        csv_reader = csv.reader(myfile, delimiter=',')
        sd_list = []
        flipped_table = [[] for _ in range(len(actual))]

        header = True
        for line in csv_reader:
            if header != True:
                for col in range(len(actual)):                
                    flipped_table[col].append(float(line[col]) - actual[col])
            header = False
    
    for row in flipped_table:
        sd_list.append(np.std(row))
        
    return sd_list