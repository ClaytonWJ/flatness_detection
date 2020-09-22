import numpy as np
import statistics
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

def process_results(results):
    indexes = [[idx, range(results[idx][0][0], results[idx][0][2]),
                           results[idx][1]] for idx in results.keys()]
    good_idxs = []
    for i in indexes:
        if not any([ranges[1] for ranges in indexes if (not ranges == i and
                                                        i[1][0] in ranges[1] and
                                                        i[1][-1] in ranges[1])]):
            good_idxs.append(i)

    return good_idxs


def print_results(results):
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

def plot_val(trace, k_r, results):

    data_points_dic = {}
    data_points = []
    segments = [(results[x][0][0], results[x][0][2]) for x in results]

    for entry in results:
        # this works when you don't run this in the function process_results()
        l_idx, _ , r_idx = results[entry][0]
        stdev = results[entry][2]

        for idx in range(l_idx, r_idx+1):
            data_points_dic[idx] = stdev

    for idx in range(len(trace)):
        if idx in data_points_dic:
            data_points.append(0)
        else:
            data_points.append(k_r[idx])

    x_points = trace
    y_points = k_r

    plt.figure(figsize=(16,8))

    plt.title("Flatness Detection")
    plt.xlabel("Trace")
    plt.ylabel("K_r")

    plt.plot(x_points, y_points)
    for seg in segments:
        plt.plot(x_points[seg[0]:seg[1]], y_points[seg[0]:seg[1]], color='r')
    # plt.colorbar()
    # plt.show()
    plt.savefig("fig_range.png")

def plot(trace, k_r, results):

    data_points_dic = {}
    data_points = []

    for entry in results:
        # this works when you don't run this in the function process_results()
        l_idx, _ , r_idx = results[entry][0]
        stdev = results[entry][2]

        for idx in range(l_idx, r_idx+1):
            data_points_dic[idx] = stdev

    for idx in range(len(trace)):
        if idx not in data_points_dic:
            data_points.append(0)
        else:
            data_points.append(1)

    x_points = trace
    y_points = k_r

    plt.figure(figsize=(16,8))

    plt.title("Flatness Detection")
    plt.xlabel("Trace")
    plt.ylabel("K_r")

    plt.scatter(x_points, y_points, c=data_points, cmap="jet", norm=Normalize(min(data_points), max(data_points)))
    plt.colorbar()
    # plt.show()
    plt.savefig("fig_range.png")

def flatness (inputTrace, indexs):
    result = {}
    buffer_size = 20
    buffer = inputTrace[0:buffer_size]
    # threshold determines the stdev value that cannot be exceded. Should consider wether to use
    # static threshold or variable (percent based increase. ie stdv < 0.01 then cannot excede 20% increase
    threshold = 0.01
    idx = buffer_size

    while (idx in indexs[buffer_size:]):
        buffer = inputTrace[(idx-buffer_size):idx]
        stdev = statistics.stdev(buffer)
        if stdev < threshold:
            # left and right used to track if buffer should expand in either direction
            left = True
            right = True
            # index of expanded buffer on right and left
            r_idx = idx
            l_idx = idx-buffer_size
            mean = sum(buffer)/len(buffer)
            allowed_range = (mean - 2*stdev, mean + 2*stdev)
            while left or right:
            # Should consider if moving right first then left each loop is ideal. What about right as far as possible
            # then left, or visa vera. Or expanding buffer at the same time.
                if right:
                    if r_idx >= len(inputTrace):
                        # stop expanding right if passed last index
                        right = False
                        continue

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

                    if allowed_range[0] <= inputTrace[l_idx] <= allowed_range[1]:
                        buffer.append(inputTrace[l_idx])
                        l_idx += 1
                    else:
                        left = False
            result[idx] = ([(l_idx+1, idx, r_idx-1), len(buffer), statistics.stdev(buffer)])
            # set idx to the last right index so the loop starts after the end of the last flat area
            idx = r_idx
        # Increment main loop index
        idx += 1
        
    return result
        
def flatness_rl (inputTrace, indexs):
    buffer_size = 20
    buffer = inputTrace[0:buffer_size]
    # threshold determines the stdev value that cannot be exceded. Should consider wether to use
    # static threshold or variable (percent based increase. ie stdv < 0.01 then cannot excede 20% increase
    threshold = 0.01
    idx = buffer_size
    result = {}

    while (idx in indexs[buffer_size:]):
        buffer = inputTrace[(idx-buffer_size):idx]
        stdev = statistics.stdev(buffer)
        if stdev < threshold:
            # left and right used to track if buffer should expand in either direction
            expanding = True
            # index of expanded buffer on right and left
            r_idx = idx
            l_idx = idx-buffer_size
            while expanding:
                r_stdev = None
                l_stdev = None
                # Check if there is data to the right, then calculate the stdev with the new point
                if r_idx < len(inputTrace):
                    r_val = buffer + [inputTrace[r_idx]]
                    r_stdev = statistics.stdev(r_val)
                    # if the point pushes the stdev over the threshold, skip this point
                    if r_stdev > threshold:
                        r_stdev = None
                        
                # Check if there is data to the left, then calculate the stdev with the new point
                if l_idx >= 0:
                    l_val = buffer + [inputTrace[l_idx]]
                    l_stdev = statistics.stdev(l_val)
                    # if the point pushes the stdev over the threshold, skip this point
                    if l_stdev > threshold:
                        l_stdev = None

                # use the data point that increases the stdev the least. If none are available the buffer is done
                if r_stdev and l_stdev:
                    if r_stdev < l_stdev:
                        buffer.append(inputTrace[r_idx])
                        r_idx += 1
                    else:
                        buffer.append(inputTrace[l_idx])
                        l_idx -= 1
                elif r_stdev:
                    buffer.append(inputTrace[r_idx])
                    r_idx += 1
                elif l_stdev:
                    buffer.append(inputTrace[l_idx])
                    l_idx -= 1
                else:
                    # add the result to the list and set the main loop idx to the further index checked
                    result[idx] = ([(l_idx+1, idx, r_idx-1), len(buffer), statistics.stdev(buffer)])
                    idx = r_idx
                    break
        # Increment main loop index
        idx += 1
    return result


if __name__ == "__main__":
    
    args = sys.argv 

    print (args)
    algorithm = "flatness"

    if len(args) == 2 and args[1] == "rl":
        algorithm = "flatness_rl"

    print('='*45)
    print('=' + ' '*15 + 'Starting Run' + ' '*16 + '=')
    print('='*45)

    # inputTrace = list(map(lambda x: round(x, 2), (np.random.rand(1,1000) *10).tolist()[0]))
    # indexs = list(range(0,len(inputTrace)))
    datafile = "Line1.csv"
    flpath = os.path.join(os.getcwd(), "example_data", datafile)

    data = open(flpath, 'r').readlines()
    formated_data = data
    headers = data[48]
    trace_k = [float(x.split(',')[3]) for x in data[50:]]
    trace = [float(x.split(',')[0]) for x in data[50:]]

    indexs = list(range(0,len(trace_k)))

    results = eval(algorithm)(trace_k, indexs)

    #print_results(process_results(results))

    # change standard deviation calculation to use a fixed average from the original buffer.
    # should make the algorithm more likely to trip threshold on gradual change.

    plot_val(trace, trace_k, results)
    
