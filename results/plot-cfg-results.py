import csv
import matplotlib.pyplot as plt
import numpy as np
from optparse import OptionParser
import math
from functools import partial

parser = OptionParser()
parser.add_option('-f', '--file', dest='filename', default='cfg-slice-test.csv', help='CSV file name')
parser.add_option('-l', '--labels', dest='labels', default='1', help='Label to plot')
parser.add_option('-w', '--avg-window', dest='wondow_size', default=1, help='Number of oints to average for a plot point')

def compute_no_nodes(w_depth):
    return 2**(w_depth + 2) - 2

def compute_no_nodes_inverse(w_depth):
    return math.log2(w_depth+2) - 2

def idt(x, func, inv):
    return func(inv(x))


def list_no_nodes(w_depths, func):
    res = []
    for wd in w_depths:
        res.append(func(wd))
    return res

def read_csv_file(file_path):
    l_depth = []
    w_depth = []
    y_values = []

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            l_depth.append(row[0])
            w_depth.append(float(row[1]))
            y_values.append(float(row[2]))

    return l_depth, w_depth, y_values

def average_data_by_label(labels, x_values, y_values, window_size=5):
    averaged_data = {}

    for label in set(labels):
        label_indices = [i for i, l in enumerate(labels) if l == label]
        label_x = [x_values[i] for i in label_indices]
        label_y = [y_values[i] for i in label_indices]
        averaged_x = []
        averaged_y = []
        for i in range(0, len(label_x), window_size):
            avg_x = np.mean(label_x[i:i+window_size])
            avg_y = np.mean(label_y[i:i+window_size])
            averaged_x.append(avg_x)
            averaged_y.append(avg_y)
        averaged_data[label] = (averaged_x, averaged_y)

    return averaged_data

(options, args) = parser.parse_args()

labels, x_values, y_values = read_csv_file(options.filename)

window_size = int(options.wondow_size)
averaged_data = average_data_by_label(labels, x_values, y_values, window_size)

plt.figure(figsize=(10, 6))
for label in averaged_data.keys():
    (avg_x, avg_y) = averaged_data[label]
    avg_x = list_no_nodes(avg_x, compute_no_nodes)
    plt.plot(avg_x, [a * 1e-9 for a in avg_y], marker='o', linestyle='-', label=f'Implementation: {label}')
plt.xlabel('Width depth')
plt.ylabel('Time Axis')
plt.title('Implementation performance difference')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
