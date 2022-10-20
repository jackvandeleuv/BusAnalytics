class AnalyzeWindow:
    def __init__(self):
        pass

    # This window allows the user to explore average frequency (gap between bus arrivals) at specific stops and routes,
    # filtered by a variety of criteria selected by the user.
    @staticmethod
    def analyze_window():
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
