# BusAnalytics

BusAnalytics is a command-line desktop application that allows you to gather and explore data describing the movement of buses in the Pittsburgh, PA bus system. Using this program, you can build a local database of bus arrivals at your favorite stops and lines, and get summary statistics about the frequency of bus arrivals.

Frequency, i.e. the length of time between bus arrivals, is an important metric for transit systems. As influential transit consultant and author Jarrett Walker has argued, "frequency is freedom." If your bus only comes every 30 minutes, you're forced to plan your schedule around the bus schedule, and you're at the mercy of early or late arrivals. Furthermore, making a trip utalizing multiple buses becomes difficult or impossible. 

For this reason, the current version of BusAnalytics focuses on frequency as the key performance metric, although support for other summary statistics may be added in the future.

# Installation

To use the program, download the project and run the .exe file.

The repository includes a 46 MB example database, which includes about a week of data collected using the application. If you don't wish to use the example database, delete the transit_data.db file.

If the program can't find a transit_data.db file in its directory, it will offer to create a new one. When the program creates a new database, it will scrape the Pittsburgh Port Authority's TrueTime API to get an up-to-date list of all stops and routes in the Pittsburgh Bus System.

# 1) Scrape new data

The first submenu allows you to scrape new data from the Pittsburgh Port Authority's TrueTime API. Select a list of routes that you want to collect data on, and a number of times for the scraping function to repeat. Once you activate the scraping process, the program will run continuously.

For every repetition of the scraping function, the program will download a snapshot of every estimated time of arrival (ETA) of every bus at every stop on each of the routes you specify. Everytime BusAnalytics completes this process, it gets a snapshot of the expected wait times for every bus and stop, which can be synthesized into summary statistics in menu 3.

# 2) Delete existing data

The second menu allows you to delete data from your database. You can delete data gathered from specific stops or routes. You can also pick certain days for which you wish to delete data (if, for whatever reason, there were some days where you used the program to scrape data that you now want to delete).

# 3) Analyse existing data

There are two main things you can do on the data analysis menu. One option is to set filters. If you're interested in seeing your data filtered by specific stops, routes, or days, you can select those options on this menu. 

After you've selected the filters you want, you can calculate average frequencies across the different ETA estimates you've collected using the first menu. This the analysis submenu currently provides several options. 

Menu option 2) calculates the average frequency (that is, the average gap between bus arrivals) for each stop in your database without taking into account routes. In other words, it shows the gaps between bus arrivals *of any kind.* If over the course of one hour, a 71A bus, an 82 bus, and a 64 bus each arrive at stop 8192, 20 minutes apart, then this option will display an average frequency of 20 minutes.

Menu option 3) shows average frequency broken out by both stop and route. There is a significant difference between this and the previous option. If you select option 3) and the same scenario as above occurs, the frequencies will be one hour for the combination of 8192 and 71A, one hour for the combination of 8192 and 82, and one hour for the combination of 8192 and 64.

Option 4) in the analysis submenu gives the overall frequency, averaged across every stop in your database, *broken out by stop only*, not route. Of course, you can apply your own filters to see how the average frequency changes for different stops, routes, and days.
