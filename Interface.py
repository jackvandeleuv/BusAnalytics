import timeit
from UpdateDB import UpdateDB
from CreateDB import CreateDB
from QueryDB import QueryDB
from DeleteDBRecords import DeleteDBRecords


class Interface:
    def __init__(self):
        pass

    def scrape_window(self):
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
                route_choice = input("To begin scraping, enter the IDs for the lines you would like to scrape "
                                     "separated by commas, like so: 71A, 71C, 65\n")
                routes_to_scrape = route_choice.split(',')
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

                    if not n_iters.isdigit():
                        print("Please enter a valid integer, indicating how many passes you would like to make through "
                              "the TrueTime website.")

                    if n_iters.isdigit():
                        n_iters = int(n_iters)
                        print(f'Scraping {routes_to_scrape}, {n_iters} times...')
                        try:
                            self.__scrape_new_data(n_iters, tuple(routes_to_scrape))
                        except RuntimeError:
                            print("There are no available routes with the given IDs.")
                        print(f"{n_iters} scrapes completed.\n")

    def __scrape_new_data(self, n_iters, routes_to_scrape):
        cnt = 0
        while cnt < n_iters:
            # Time each loop so the user can see an updated count of how long each pass through the website takes.
            start = timeit.default_timer()
            # Use the scrape_estimates method to gather and process the data.
            estimates = UpdateDB.scrape_estimates(routes_to_scrape)
            if estimates is not None:
                # If data was returned successfully, enter it into the transit_data database.
                UpdateDB.update_db(estimates)
            stop = timeit.default_timer()
            print('Successfully captured a snapshot of all relevant routes/stops, taking', round(stop - start), 'seconds.')
            cnt = cnt + 1

    # If the user selected the option to delete all data from specific stops, this function is called.
    def __delete_by_stops(self):
        print('Currently you have these stops in your database:\n')
        # Inform the user about what stops are currently in the database. QueryDB executes a SQLite query.
        stops = QueryDB.get_scraped_stops()
        for stop in stops:
            print(stop)
        choice2a = input("Select which stops you'd like to delete data for (for multiple stops, separate by commas: ")

        print(f'Deleting all data for {choice2a}')
        # Process the user input. If they entered comma-separated values, this block is triggered, which cleans up the
        # input.
        if ',' in choice2a:
            stops_to_delete = choice2a.split(',')
            for i in range(len(stops_to_delete)):
                stops_to_delete[i] = stops_to_delete[i].strip()

        # If one stop was entered, strip off the white space and wrap it in a list.
        if ',' not in choice2a:
            stops_to_delete = [choice2a.strip()]

        # Pass the list of stops to delete_by_criteria, which deletes all data points matching those routes.
        DeleteDBRecords.delete_by_stops(stops_to_delete)

        print(f'Successfully deleted all data for {choice2a}')

    # If the user selected the option to delete all data from specific routes, this function is called.
    def __delete_by_routes(self):
        print('Currently you have these routes in your database:\n')
        # Inform the user about what stops are currently in the database. QueryDB executes a SQLite query.
        routes = QueryDB.get_scraped_routes()
        for route in routes:
            print(route)

        choice2b = input("Select which routes you'd like to delete data for: ")

        print(f'Deleting all data for {choice2b}')

        # Process the user input. If they entered comma-separated values, this block is triggered, which cleans up the
        # input.
        if ',' in choice2b:
            routes_to_delete = choice2b.split(',')
            for i in range(len(routes_to_delete)):
                routes_to_delete[i] = routes_to_delete[i].strip()

        # If one route was entered, strip off the white space and wrap it in a list.
        if ',' not in choice2b:
            routes_to_delete = [choice2b.strip()]

        # Pass the list of routes to delete_by_criteria, which deletes all data points matching those routes.
        DeleteDBRecords.delete_by_lines(routes_to_delete)

        print(f'Successfully deleted all data for {choice2b}')

    # If the user selected the option to delete all data from specific dates, this function is called.
    def __delete_by_dates(self):
        print('Currently you have data from these days in your database:')
        # Inform the user about what dates are currently in the database. QueryDB executes a SQLite query.
        days = QueryDB.get_scraped_days()
        for day in days:
            print(day)

        choice2c = input(
            "Enter the dates you'd like to delete data for, separated by commas (e.g. 2020-10-05, 2020-10-07): ")

        print(f'Deleting all data for {choice2c}')
        # Process the user input. If they entered comma-separated values, this block is triggered, which cleans up the
        # input.
        if ',' in choice2c:
            dates_to_delete = choice2c.split(',')
            for i in range(len(dates_to_delete)):
                dates_to_delete[i] = dates_to_delete[i].strip()

        # If one date was entered, strip off the white space and wrap it in a list.
        if ',' not in choice2c:
            dates_to_delete = [choice2c.strip()]

        # Pass the list of dates to delete_by_criteria, which deletes all data points matching those dates.
        DeleteDBRecords.delete_by_dates(dates_to_delete)

        print(f'Successfully deleted all data for {choice2c}')

    def delete_window(self):
        request_return = False

        while not request_return:
            # Get the list of all tuples in the ESTIMATES table.
            n_records = QueryDB.count_estimates()[0][0]

            choice1 = input(f"\nWelcome to the delete menu. Enter 'RETURN' to return to the main menu.\n"
                            f"You currently have {n_records} scraped data points in your database.\n\nIf you want to wipe "
                            f"your database and update the routes in your database based on the Pittsburgh Port Authority's "
                            f"TrueTime website, enter DELETE ALL, or pick what criteria you'd like to delete by (enter "
                            f"STOP_ID, ROUTE_ID, DATES): ")

            if choice1 == 'RETURN':
                return

            # If the user selects DELETE ALL, drop all existing tables and scape an updated list of stop names and route
            # names from the TrueTime website, which will be the basis of any future scraping.
            if choice1 == 'DELETE ALL':
                print("Deleted database. Scraping the TrueTime website to find an updated set of stops and routes...\n")
                CreateDB.reset_db_with_new_stops_n_routes()
                print("Done. You database has been wiped clean and updated with the latest routes/stops!\n")
                return

            # These three functions provide a similar feature, which allows the user to delete all ESTIMATES tuples matching
            # stops, routes, or dates respectively.
            if choice1 == 'STOP_ID':
                self.__delete_by_stops()

            if choice1 == 'ROUTE_ID':
                self.__delete_by_routes()

            if choice1 == 'DATES':
                self.__delete_by_dates()

    # This window allows the user to explore average frequency (gap between bus arrivals) at specific stops and routes,
    # filtered by a variety of criteria selected by the user.
    def analyze_window(self):
        # This set contains all the dates (each date is a str formatted like '2022-10-10') that we would like to use in our
        # calculation of the average frequency.
        limit_by_days = set()

        sports_op = input("Show only data from days when sports games are happening in the area? (YES/NO): ")

        if sports_op == 'YES':
            # get_sports_schedule returns a list of dicts, they key for each date being a day when a local sports game is
            # occurring.
            sports_dict = get_sports_schedule()
            for dictionary in sports_dict:
                for key in dictionary:
                    # Validate input for correct date format.
                    if len(key) == 10 and type(key) == str:
                        limit_by_days.add(key)

        weather_op = input("Filter by weather similar to today? (YES/NO)")

        weather_dates = []
        if weather_op == 'YES':
            # weather_dates returns a list of dates with weather similar to today's weather.
            weather_dates = get_matching_weather_dates()
            for weather_date in weather_dates:
                if len(weather_date) == 10 and type(weather_date) == str:
                    limit_by_days.add(weather_date)

        print("\nThe routes you have scraped data for in your database are:")
        # Get list of all unique ROUTE_IDs in the ESTIMATES table, reflecting all routes for which we have ETA data.
        scraped_routes = QueryDB.get_scraped_routes()
        for route in scraped_routes:
            print(route)

        route_op = input("Select a route (you can only select one route, and you must select one): ")

        route = route_op.strip()

        see_stops = input(
            "Would you like to see a list of available stops (with associated routes) in your database of scraped data? (YES/NO): ")

        if see_stops == "YES":
            # This is an extra option, which allows users to see all stops matching the given route for which we have ETA
            # data.
            scraped_stops = QueryDB.get_scraped_stops_based_on_route(route)
            for stop in scraped_stops:
                id = stop[0]
                name = stop[1]
                print(f'You have data for Stop {id} aka {name} on Route {route}')

        stop_op = input(
            "Select data from these stops (Separate your stop_ids with commas. If you want them all, enter ALL): ")

        # If the user isn't filtering by stop, get all the stops for which we have ETA data on the given route and add them
        # to stop_list.
        if stop_op == 'ALL':
            stops_and_names = QueryDB.get_scraped_stops_based_on_route(route)
            stop_list = [x[0] for x in stops_and_names]

        # If the user entered specific stop(s), clean the input and add the list of STOP_IDs to stop_list.
        if stop_op != 'ALL':
            if ',' in stop_op:
                stop_list = stop_op.split(',')
                for i in range(len(stop_list)):
                    stop_list[i] = int(stop_list[i].strip())
            if ',' not in stop_op:
                stop_list = [int(stop_op.strip())]

        print('Calculating average frequency based on entered parameters...')

        # .get_scraped_days() finds all days for which we have ETA data.
        scraped_days_list = QueryDB.get_scraped_days()
        scraped_days_set = set(scraped_days_list)

        # Use a set operation to find the days that we have data for which are also days contained in the limit_by_days
        # list, which, depending on user input, may have days with sports games occurring or dates with similar weather.
        if len(limit_by_days) != 0:
            scraped_days_set = list(scraped_days_set.intersection(limit_by_days))

        # If the filtering criteria didn't leave any days, return to the main menu.
        if len(scraped_days_set) == 0:
            print('Your filtering criteria didn\t return any days that matched the data you have scraped!')
            return

        print('These days are being used in the calculation: ', scraped_days_set)

        # Get the officially-reported on-time percentage for the route and list of days we've selected.
        official_on_times = get_on_time_percent(scraped_days_set, route)

        # Pass three parameter to this module. Each should either be a list of values, or an empty indicating "all" for that criterion
        averages = filtered_wait_time_averages_stops(stop_list, route, scraped_days_set)

        total = 0
        # Averages is a dictionary with {STOP_ID: average frequency}.
        if averages:
            for key, value in averages.items():
                print(f'The average frequency at stop: {key} over the selected period is {value}')

            for key, value in official_on_times.items():
                print(f'\nOver the last five years, the officially-reported average on-time percentage in {key} were:\n'
                      f'Saturdays: {value.loc["SAT."]}\nSundays: {value.loc["SUN."]}\nWeekdays: {value.loc["WEEKDAY"]}')

