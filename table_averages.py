import csv

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
