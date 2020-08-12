import numpy as np
import statistics

print('='*45)
print('=' + ' '*15 + 'Starting Run' + ' '*16 + '=')
print('='*45)

#inputTrace = list(map(lambda x: round(x, 2), (np.random.rand(1,1000) *10).tolist()[0]))
#indexs = list(range(0,len(inputTrace)))

flpath = r'C:\Users\Clayt\Desktop\scripts\Line1.csv'

data = open(flpath, 'r').readlines()
formated_data = data
headers = data[48]
trace_k = [float(x.split(',')[3]) for x in data[50:]]

indexs = list(range(0,len(trace_k)))
#print(inputTrace)
# change standard deviation calculation to use a fixed average from the original buffer.
# should make the algorithm more likely to trip threshold on gradual change.

def flatness (inputTrace, indexs):
    buffer_size = 5
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
            print("=====================")
            print(stdev)
            # index of expanded buffer on right and left
            r_idx = idx
            l_idx = idx-buffer_size-1
            while left or right:
            # Should consider if moving right first then left each loop is ideal. What about right as far as possible
            # then left, or visa vera. Or expanding buffer at the same time.
                if right:
                    if r_idx >= len(inputTrace):
                        # stop expanding right if passed last index
                        right = False
                        continue
                    # add next item on the right to the  buffer and recalculate stdev, remove the item if it fails
                    # the threshold and stop expanding right
                    buffer.append(inputTrace[r_idx])
                    stdev = statistics.stdev(buffer)
                    r_idx += 1
                    if stdev >= threshold:
                        right = False
                        buffer = buffer[:-1]
                if left:
                    if l_idx < 0:
                        # stop expanding left if past first index
                        left = False
                        continue
                    # add next item on the left to the buffer and recalculate stdev, remove the item if it fails 
                    # the threshold and stop expanding left
                    buffer.insert(0, inputTrace[l_idx])
                    stdev = statistics.stdev(buffer)
                    l_idx -= 1
                    if stdev >= threshold:
                        left = False
                        buffer = buffer[1:]
            # set idx to the last right index so the loop starts after the end of the last flat area
            idx = r_idx
            # Log information about the buffer
            print("Buffer size = " + str(len(buffer)))
            print(stdev)
            print(l_idx)
            print(idx)
            print(r_idx)
        # Increment main loop index
        idx += 1
        


flatness(trace_k, indexs)

    
