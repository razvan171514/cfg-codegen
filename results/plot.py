import os
import csv
import matplotlib.pyplot as plt
from optparse import OptionParser

def read_csv_file(file_path):
    data = []
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return data

def filter_data(data, label, label_value):
    return [row for row in data if row[label] == label_value]

parser = OptionParser()
parser.add_option('-f', '--file', dest='filename', default='results-cg-slice.csv', help='CSV file name')
parser.add_option('-x', '--plot-x', dest='plot_x', default='', help='X axis label')
parser.add_option('-y', '--plot-y', dest='plot_y', default='', help='Y axis label')
parser.add_option('-n', '--label-name', dest='label_column', default='vertices', help='The name of the column that represents the label to plot.')
parser.add_option('-l', '--labels', dest='labels', default='25,26', help='Label to plot. Must be comma sepparated label values')

parser.add_option('-w', '--avg-window', dest='wondow_size', default=5, help='Number of points to average for a plot point')
(options, args) = parser.parse_args()

data = read_csv_file(options.filename)

for label in options.labels.split(','):
    labeled_data = sorted(filter_data(data, options.label_column, label), key=lambda x: int(x[options.plot_x]))
    x_vals = [int(row[options.plot_x]) for row in labeled_data]
    y_vals = [int(row[options.plot_y]) for row in labeled_data]

    plt.plot(x_vals, y_vals, label=f"Label: {label}")

plt.xlabel(options.plot_x)
plt.ylabel(options.plot_y)
plt.title(f"{options.plot_x} vs {options.plot_y} for different {options.label_column}")
plt.legend()
plt.grid(True)
plt.show()
