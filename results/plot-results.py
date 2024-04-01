import csv
import matplotlib.pyplot as plt
import numpy as np
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-f', '--file', dest='filename', default='callgraph-slice-test.csv', help='CSV file name')
parser.add_option('-l', '--labels', dest='labels', default='25,26', help='Label to plot')
parser.add_option('-w', '--avg-window', dest='wondow_size', default=5, help='Number of oints to average for a plot point')

def read_csv_file(file_path):
    labels = []
    x_values = []
    y_values = []

    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            labels.append(row[0])
            x_values.append(float(row[1]))
            y_values.append(float(row[2]))

    return labels, x_values, y_values

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
for label in options.labels.split(','):
    (avg_x, avg_y) = averaged_data[label]
    plt.plot(avg_x, avg_y, marker='o', linestyle='-', label=f'No nodes: {label}')
plt.xlabel('No edges Axis')
plt.ylabel('Time Axis')
plt.title('Averaged Scatter Plot with Connecting Lines by Label')
plt.legend()
plt.grid(True)
plt.show()
