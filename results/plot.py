import os
import csv
import matplotlib.pyplot as plt
import numpy as np
from optparse import OptionParser

def read_csv_file(file_path):
    data = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data

def average_data(data, window_size):
    averaged_x = []
    averaged_y = []
    for i in range(0, len(data[0]), window_size):
        avg_x = np.mean(data[0][i:i+window_size])
        avg_y = np.mean(data[1][i:i+window_size])
        averaged_x.append(avg_x)
        averaged_y.append(avg_y)
    return averaged_x, averaged_y

def filter_data(data, label, label_value):
    return [row for row in data if row[label] == label_value]

parser = OptionParser()
parser.add_option('-f', '--file', dest='filename', default='results-cg-slice.csv', help='CSV file name')
parser.add_option('-x', '--plot-x', dest='plot_x', default='', help='X axis label')
parser.add_option('-y', '--plot-y', dest='plot_y', default='', help='Y axis label')
parser.add_option('-n', '--label-name', dest='label_column', default='vertices', help='The name of the column that represents the label to plot.')
parser.add_option('-l', '--labels', dest='labels', default='25,26', help='Label to plot. Must be comma sepparated label values')
parser.add_option('-w', '--avg-window', dest='window_size', default=5, help='Number of points to average for a plot point')
parser.add_option('-c', '--compare', dest='compare', action="store_true", default=False, help='Compare result form -f file with the one from -a file')
parser.add_option('-a', '--against-file', dest='against_filename', default='results-cg-slice.csv', help='CSV file name to compare -f with')
(options, args) = parser.parse_args()

window_size = int(options.window_size)

data = read_csv_file(options.filename)

if options.compare:
    against_data = read_csv_file(options.against_filename)

for label in options.labels.split(','):
    labeled_data = sorted(filter_data(data, options.label_column, label), key=lambda x: int(x[options.plot_x]))
    x_vals = [int(row[options.plot_x]) for row in labeled_data]
    y_vals = [int(row[options.plot_y]) for row in labeled_data]
    avg_x, avg_y = average_data((x_vals, y_vals), window_size)
    
    plt.plot(avg_x, avg_y, label=f"Label: {label} {options.filename}")
    
    if options.compare:
        labeled_against_data = sorted(filter_data(against_data, options.label_column, label), key=lambda x: int(x[options.plot_x]))
        x_a_vals = [int(row[options.plot_x]) for row in labeled_against_data]
        y_a_vals = [int(row[options.plot_y]) for row in labeled_against_data]
        avg_a_x, avg_a_y = average_data((x_a_vals, y_a_vals), window_size)
        plt.plot(avg_a_x, avg_a_y, label=f"Label: {label} {options.against_filename}")
    

plt.xlabel(options.plot_x)
plt.ylabel(options.plot_y)
plt.title(f"{options.plot_x} vs {options.plot_y} for different {options.label_column}")
plt.legend()
plt.grid(True)
plt.show()
