import numpy as np
import datetime
import statistics
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

def remove_duplicate_ranges(results):
    '''
    Function to remove duplicate flat areas. It checks if any set of indexes are completely contained inside another set
    and removes them if this is true. It them adds the valid results into a dictionary with the starting index as the key
    :param results:
    :return: result dictionary in form {"<starting index>": [(<min index>, <start index>, <max index>), # indexes]
    '''
    # convert the input results into a lists with the starting index and a range between the min and max index of the
    # flat area
    indexes = [[idx, range(results[idx][0][0], results[idx][0][2]),
                           results[idx][1]] for idx in results.keys()]
    good_idxs = {}
    # Check if any result's range is contained completely within any of the other results. If so, remove it as its
    # a redundant result
    for i in indexes:
        if not any([ranges[1] for ranges in indexes if (not ranges == i and
                                                        i[1][0] in ranges[1] and
                                                        i[1][-1] in ranges[1])]):
            good_idxs[i[0]] = [(i[1][0], i[0], i[1][-1]), i[2]]

    # Return the filtered results in a dictionary format
    return good_idxs


def print_results(results):
    '''
    Function to print out results in a nice format
    :param results:
    :return:
    '''
    for entry in results:
        if isinstance(entry, dict):
            print('+'*20)
            print("Starting Index: " + str(entry))
            print("Indexes: " + str(results[entry][0]))
            print("Buffer Size: " + str(results[entry][1]))
        else:
            print('+'*20)
            print("Starting Index: " + str(entry[0]))
            print("Indexes: " + str(entry[1]))
            print("Buffer Size: " + str(entry[2]))

def plot_val(trace, k_r, results, save_figure=False, fig_name="flatness", fig_type="png"):
    '''
    Function to plot the results of the algorithm using matplotlib. The function will create a line plot of the original
    data (x = trace number, y = Plot parameter) and plot the indexes identified as flat overtop the original data in red.
    :param trace: List of Trace Numbers
    :param k_r: List of Values
    :param results: Result dictionary from flatness algorithm
    :return:
    '''
    # data_points_dic = {}
    # data_points = []
    segments = [(results[x][0][0], results[x][0][2]) for x in results]

    x_points = trace
    y_points = k_r

    plt.figure(figsize=(16,8))

    plt.title("Flatness Detection")
    plt.xlabel("Trace")
    plt.ylabel("K_r")
    plt.ylim((0,5))

    plt.plot(x_points, y_points)
    for seg in segments:
        plt.plot(x_points[seg[0]:seg[1]], y_points[seg[0]:seg[1]], color='r')

    if save_figure:
        plt.savefig(fig_name + "." + fig_type)
    else:
        plt.show()

    plt.close()

def flatness (inputTrace, indexs):
    '''
    Algorithm designed to identify flat areas within a pdp line dataset. The algorithm uses a set buffer size and a
    threshold for standard deviation to identify flat areas. If the points within the buffer are under the threshold it
    then trys to expand the buffer to the left and right as much as possible by check if the next point has a value
    equal to or less than 2 standard deviations away from the mean of the original buffer points. Once it fails this
    condition in both directions it returns the result.
    :param inputTrace:
    :param indexs:
    :return:
    '''
    result = {}
    # Buffer size controls and number of points that are checked at once. It is the minimum # of points that used to
    # check if an area is considered flat
    buffer_size = 20
    # threshold determines the standard deviation value that is checked to determine if an area is flat
    threshold = 0.05
    idx = buffer_size

    while (idx in indexs[buffer_size:]):
        # Set the buffer to the x number of points before the current index
        buffer = inputTrace[(idx-buffer_size):idx]
        # number of standard deviation to consider valid
        stdv_factor = 3
        # calculate the standard deviation on the point within the buffer and check if it meats the threshold condition
        stdev = statistics.stdev(buffer)
        if stdev < threshold:
            # left and right used to track if buffer should expand in either direction
            left = True
            right = True
            # index of expanded buffer on right and left
            r_idx = idx + 1
            l_idx = idx-buffer_size

            mean = sum(buffer)/len(buffer)
            # Calculate 2 standard deviations above and below and use it as the range of accepted values
            allowed_range = (mean - stdv_factor*threshold, mean + stdv_factor*threshold)
            while left or right:
                # Expansion loop. This loop will attempt to add points to the existing buffer based on if the new point
                # is within the allowed_range. When it cannot expand further it returns the resulting list of points
                if right:
                    if r_idx >= len(inputTrace):
                        # stop expanding right if passed last index
                        right = False
                        continue
                    # if the value is within the allowed_range add it to the buffer and move the right index
                    if allowed_range[0] <= inputTrace[r_idx] <= allowed_range[1]:
                        buffer.append(inputTrace[r_idx])
                        r_idx += 1
                    else:
                        right = False
                if left:
                    if l_idx < 0:
                        # stop expanding left if past first index
                        left = False
                        continue
                    # if the value is within the allowed_range add it to the buffer and move the left index
                    if allowed_range[0] <= inputTrace[l_idx] <= allowed_range[1]:
                        buffer.append(inputTrace[l_idx])
                        l_idx -= 1
                    else:
                        left = False
            # remove the +/- from left and right index because it always ends on a failed check
            result[idx] = ([(l_idx+1, idx, r_idx-1), len(buffer), statistics.stdev(buffer)])
            # set idx to the last right index + buffer size so the main loop checks the next new points in the dataset
            idx = r_idx + buffer_size - 1
        # Increment main loop index
        idx += 1
        
    return result


if __name__ == "__main__":
    
    args = sys.argv 

    algorithm = "flatness"

    if len(args) == 2 and args[1] == "md":
        algorithm = "flatness_mean_diff"

    print('='*45)
    print('=' + ' '*15 + 'Starting Run' + ' '*16 + '=')
    print('='*45)
    start_time = datetime.datetime.now()

    # inputTrace = list(map(lambda x: round(x, 2), (np.random.rand(1,1000) *10).tolist()[0]))
    # indexs = list(range(0,len(inputTrace)))
    in_files = [x for x in os.listdir(os.path.join(os.getcwd(), "example_data")) if "Line" in x]
    for fl in in_files:
        datafile = fl
        flpath = os.path.join(os.getcwd(), "example_data", datafile)

        data = open(flpath, 'r').readlines()
        formated_data = data
        if 'verbose' in datafile:
            headers = data[0]
            trace_k = [float(x.split(',')[3]) for x in data[1:]]
            trace = [float(x.split(',')[0]) for x in data[1:]]
        else:
            headers = data[48]
            trace_k = [float(x.split(',')[3]) for x in data[50:]]
            trace = [float(x.split(',')[0]) for x in data[50:]]

        indexs = list(range(0,len(trace_k)))

        results = eval(algorithm)(trace_k, indexs)

        processed_results = remove_duplicate_ranges(results)

        plot_val(trace, trace_k, processed_results, save_figure=True, fig_name=datafile.split('.')[0])

    end_time = datetime.datetime.now()
    time_delta = end_time - start_time
    print ("S: {} - E: {}\nRun time: {:.2f}s".format(start_time, end_time, (time_delta.total_seconds())))
    
