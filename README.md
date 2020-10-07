# flatness_detection

The flatness_decction project was designed to identify flat areas within a pdp line dataset. The detection algorithm uses a set buffer size and a
threshold for standard deviation to identify flat areas. It checks over the entire dataset with a moving window that looks at a number of points equal to the buffer size. If the standard deviation of the points within the buffer are under the threshold that segment is considered flat. 

The algorithm then trys to expand the buffer to the left and right of the initial points as much as possible by checking if the next point has a value
equal to or less than 2 standard deviations away from the mean of the original buffer points. Once it fails this condition in both directions it returns the resulting extent of the flat area. 

The results are then processed to remove any duplicate areas / flat area that are completely contained with another and it generates a final result which is up to 4 flat areas within the dataset. The 4 results are the minimum average value flat area, the average average value flat area, the maximum average value flat area and the longest flat area.

![example_plot1](example_plot1.png?raw=true)


![example_plot2](example_plot2.png?raw=true)


![example_plot3](example_plot3.png?raw=true)
