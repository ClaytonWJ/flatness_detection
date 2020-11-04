# flatness_detection

The flatness_decction project was designed to identify flat areas within a pdp line dataset. The detection algorithm uses a set buffer size and a
threshold for standard deviation to identify flat areas. It checks over the entire dataset with a moving window that looks at a number of points equal to the buffer size. If the standard deviation of the points within the buffer are under the threshold that segment is considered flat. 

The algorithm then trys to expand the buffer to the left and right of the initial points as much as possible by checking if the next point has a value
equal to or less than 2 standard deviations away from the mean of the original buffer points. Once it fails this condition in both directions it returns the resulting extent of the flat area. 

The results are then processed to remove any duplicate areas / flat area that are completely contained with another and it generates a final result which is up to 4 flat areas within the dataset. The 4 results are the minimum average value flat area, the average average value flat area, the maximum average value flat area and the longest flat area.

#### Each plot can show up to 4 flat areas, each with a different colour to represent them. 
 - Red is the maximum average value for flat areas
 - Orange is the average of average values for flat areas
 - Yellow is the minimum average value for flat areas
 - Cyan is the longest flat area (# of points)

##### Plot of PDP data collected over a new asphalt patch. The line covers a section of old asphalt, which transitions to the patch, then back to old asphalt
![example_plot1](Images/example_plot1.png?raw=true)


##### Plot with more "noisy" data
![example_plot2](Images/example_plot2.png?raw=true)


#### Plot with only 1 flat area found
![example_plot3](Images/example_plot3.png?raw=true)


#### Plot of data collected during bench test indoors
![example_plot3](Images/example_plot4.png?raw=true)
