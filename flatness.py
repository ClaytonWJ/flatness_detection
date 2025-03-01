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
    good_idxs = {}
    # Check if any result's range is contained completely within any of the other results. If so, remove it as its
    # a redundant result
    result_ranges = [range(results[idx][0][0], results[idx][0][2]) for idx in results]
    for idx in results:
        c_range = range(results[idx][0][0], results[idx][0][2])
        if not any(ranges for ranges in result_ranges if (not ranges == c_range and c_range[0] in ranges and c_range[-1] in ranges)):
            good_idxs[idx] = results[idx] 

    # Return the filtered results in a dictionary format
    return good_idxs


def generate_results(results):

    longest_flat_area = max(results, key=lambda k: results[k][1])
    max_flat_area = max(results, key=lambda k: results[k][3])
    min_flat_area = min(results, key=lambda k: results[k][3])

    average_val = sum([results[val][3] for val in results]) / len(results)

    average_flat_area = min(results, key=lambda k: abs(results[k][3] - average_val))

    return {'max': results[max_flat_area], 
            'min': results[min_flat_area], 
            'average': results[average_flat_area],
            'longest': results[longest_flat_area]}


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

def plot_val(trace, k_r, results, generated_results={}, save_figure=False, **kwargs):
    '''
    Function to plot the results of the algorithm using matplotlib. The function will create a line plot of the original
    data (x = trace number, y = Plot parameter) and plot the indexes identified as flat overtop the original data in red.
    :param trace: List of Trace Numbers
    :param k_r: List of Values
    :param results: Result dictionary from flatness algorithm
    :return:
    '''

    fig_name = kwargs.get('fig_name', "flatness")
    fig_type = kwargs.get('fig_type', "png")
    buffer_size = kwargs.get('buffer_size', None)
    threshold = kwargs.get('threshold', None)

    segments = [(results[x][0][0], results[x][0][2]) for x in results]

    x_points = trace
    y_points = k_r

    plt.figure(figsize=(16,8))

    plt.title("Flatness Detection - Buffer: {}, Threshold: {}".format(buffer_size, threshold))
    plt.xlabel("Trace")
    plt.ylabel("K_r")
    plt.ylim((0, 8))

    plt.plot(x_points, y_points)

    if generated_results:
        if generated_results.get('longest'):
            idx = generated_results['longest'][0]
            plt.plot(x_points[idx[0]:idx[2]], y_points[idx[0]:idx[2]], color='c')
        if generated_results.get('max'):
            idx = generated_results['max'][0]
            plt.plot(x_points[idx[0]:idx[2]], y_points[idx[0]:idx[2]], color='r')
        if generated_results.get('min'):
            idx = generated_results['min'][0]
            plt.plot(x_points[idx[0]:idx[2]], y_points[idx[0]:idx[2]], color='yellow')
        if generated_results.get('average'):
            idx = generated_results['average'][0]
            plt.plot(x_points[idx[0]:idx[2]], y_points[idx[0]:idx[2]], color='tab:orange')
    else:
        for seg in segments:
            plt.plot(x_points[seg[0]:seg[1]], y_points[seg[0]:seg[1]], color='r')

    if save_figure:
        plt.savefig(fig_name + "." + fig_type)
    else:
        plt.show()

    plt.close()

def flatness (inputTrace, indexs, mode="restrictive"):
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
    # The flatness tolerances contains tuples of value pairs, buffer size (first value) and threshold (second value)
    # Buffer size controls and number of points that are checked at once. It is the minimum # of points that used to
    # determine if an area is considered flat
    # threshold determines the standard deviation value that is checked to determine if an area is flat
    flatness_tolerances = {"restrictive": [(20, 0.05), (20, 0.1), (10, 0.05), (10, 0.1), (5, 0.1)]}

    for buffer_size, threshold in flatness_tolerances[mode]:
        # print("*--------- Determining flat areas using Buffer size: {} and Threshold: {} ---------*".format(buffer_size, threshold))
        idx = buffer_size
        while (idx in indexs[buffer_size:]):
            # Set the buffer to the x number of points before the current index
            buffer = inputTrace[(idx-buffer_size):idx]
            # number of standard deviation to consider valid
            stdv_factor = 2
            # calculate the standard deviation on the point within the buffer and check if it meats the threshold condition
            stdev = statistics.stdev(buffer)
            if stdev < threshold:
                # left and right used to track if buffer should expand in either direction
                left = True
                right = True
                # index of expanded buffer on right and left
                r_idx = idx
                l_idx = idx-buffer_size

                mean = sum(buffer)/len(buffer)
                # Calculate 2 standard deviations above and below and use it as the range of accepted values
                allowed_range = (mean - stdv_factor*threshold, mean + stdv_factor*threshold)
                while left or right:
                    # Expansion loop. This loop will attempt to add points to the existing buffer based on if the new point
                    # is within the allowed_range. When it cannot expand further it returns the resulting list of points
                    if right:
                        r_idx += 1
                        if r_idx >= len(inputTrace):
                            # stop expanding right if passed last index
                            right = False
                            continue
                        # if the value is within the allowed_range add it to the buffer and move the right index
                        if allowed_range[0] <= inputTrace[r_idx] <= allowed_range[1]:
                            buffer.append(inputTrace[r_idx])
                        else:
                            right = False
                    if left:
                        l_idx -=1
                        if l_idx < 0:
                            # stop expanding left if past first index
                            left = False
                            continue
                        # if the value is within the allowed_range add it to the buffer and move the left index
                        if allowed_range[0] <= inputTrace[l_idx] <= allowed_range[1]:
                            buffer.append(inputTrace[l_idx])
                        else:
                            left = False
                # remove the +/- from left and right index because it always ends on a failed check
                result[idx] = ([(l_idx+1, idx, r_idx-1), len(buffer), statistics.stdev(buffer), sum([abs(val) for val in buffer])/len(buffer)])
                # set idx to the last right index + buffer size so the main loop checks the next new points in the dataset
                idx = r_idx + buffer_size - 1
            # Increment main loop index
            idx += 1
            
        if result:
            return result, buffer_size, threshold
        else:
            print("*--------- Failed to find any flat areas ---------*")


if __name__ == "__main__":
    
    args = sys.argv 

    algorithm = "flatness"

    # if len(args) == 2 and args[1] == "md":
    #     algorithm = "flatness_mean_diff"

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

        print("*--------- Processing data from {} ---------*".format(fl))

        results = eval(algorithm)(trace_k, indexs)

        if not results:
            print("RUN HAS FAILED TO FIND ANYTHING!")
        else:
            # unpack the results
            results, buffer_size, threshold = results
            processed_results = remove_duplicate_ranges(results)

            generated_results = generate_results(processed_results)

            plot_val(trace, trace_k, processed_results, generated_results=generated_results, save_figure=True,
                     fig_name=datafile.split('.')[0], buffer_size=buffer_size, threshold=threshold)

    end_time = datetime.datetime.now()
    time_delta = end_time - start_time
    print ("S: {} - E: {}\nRun time: {:.2f}s".format(start_time, end_time, (time_delta.total_seconds())))
    print ("Processed {} files...".format(len(in_files)))
    
