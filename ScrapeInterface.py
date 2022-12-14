import time
import timeit
from UpdateDB import UpdateDB
from QueryDB import QueryDB


class ScrapeInterface:
    @staticmethod
    def scrape_window():
        # Loop through the options in this sub-menu until the user requests to return to the main menu.
        while True:
            user_input = input("***Scrape New Data***\n0) Return to Main Menu\n1) See a list of routes available to "
                               "scrape.\n2) Scrape new data.\n")

            if not user_input.isdigit():
                print("\nPlease enter an integer to select one of the menu options.\n")

            if int(user_input) == 0:
                return

            # Query the db for all routes where ESTIMATE data has been previously scraped.
            if int(user_input) == 1:
                available_routes = QueryDB.get_available_routes()
                print("***Available Routes***")
                for route in available_routes:
                    id = route[0]
                    name = route[1]
                    print("ROUTE_ID: {:4s} (Name: {:s})".format(id, name))

            # Take the user input. If the user entered comma-separated values, split the values and remove white-space.
            if int(user_input) == 2:
                route_choice = input("To begin scraping, enter the IDs for the routes you would like to scrape "
                                     "separated by commas, like so: 71A, 71C, 65\n")
                routes_to_scrape = route_choice.split(',')

                # routes_valid checks whether the user-selected routes are five characters or fewer, which is the
                # maximum size for a valid route name.
                routes_valid = True
                # Strip off the trailing spaces from the user input.
                for i in range(len(routes_to_scrape)):
                    routes_to_scrape[i] = routes_to_scrape[i].strip()
                    routes_to_scrape[i] = routes_to_scrape[i].upper()
                    # Check to make sure that the route IDs entered are not too long, which indicates an invalid
                    # route ID.
                    if len(routes_to_scrape[i]) > 5:
                        routes_valid = False

                if not routes_valid:
                    print("Sorry, the system could not recognize one of the route names you entered.")

                # Ask the user how many times they want to make a pass through the TrueTime website to scrape more data.
                if routes_valid:
                    n_iters = input("Got it! How many times would you like to scrape the TrueTime website? On average, "
                                    "it takes about 45 seconds per route, per scrape. Enter an int:\n")

                    # Check if the user-entered value is an integer.
                    if not n_iters.isdigit():
                        print("Please enter a valid integer, indicating how many passes you would like to make through "
                              "the TrueTime website.")

                    if n_iters.isdigit():
                        n_iters = int(n_iters)
                        print(f'Scraping {routes_to_scrape}, {n_iters} times...')
                        # This method executes a loop, scraping the TrueTime website and gathering information for each
                        # stop on a route requested by the user. n_iters is the number of times the function will loop.
                        try:
                            ScrapeInterface.__scrape_new_data(n_iters, tuple(routes_to_scrape))
                            print(f"{n_iters} scrapes completed.\n")
                        except RuntimeError:
                            print("There are no available routes with the given IDs.")

    @staticmethod
    def __scrape_new_data(n_iters, routes_to_scrape):
        cnt = 0
        # Each pass through the TrueTime website is given a unique scrape_id which is the UNIX timestamp at the moment
        # the scrape began. The scrape_id will be the same for all ESTIMATES rows generated by each loop.
        scrape_id = time.time()
        while cnt < n_iters:
            # Time each loop so the user can see an updated count of how long each pass through the website takes.
            start = timeit.default_timer()
            # Use the scrape_estimates method to gather and process the data.
            estimates = UpdateDB.scrape_estimates(routes_to_scrape, scrape_id)
            if estimates is None:
                print("Something went wrong. No data was returned by this attempt!")
            if estimates is not None:
                # If data was returned successfully, enter it into the transit_data database.
                UpdateDB.update_db(estimates)
            stop = timeit.default_timer()
            print('One cycle completed, taking', round(stop - start), 'seconds.')
            cnt = cnt + 1
