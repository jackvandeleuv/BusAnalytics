from CreateDB import CreateDB
from QueryDB import QueryDB
from DeleteDBRecords import DeleteDBRecords


class DeleteInterface:
    def __init__(self):
        pass

    # If the user selected the option to delete all data from specific stops, this function is called.
    @staticmethod
    def __delete_by_stops():
        while True:
            user_input = input(
                "***Delete By STOP_ID***\n0) Return to Delete Menu.\n1) See all stops in your database.\n"
                "2) Enter IDs and delete data.\n")

            if not user_input.isdigit():
                print("\nPlease enter an integer to select one of the menu options.\n")

            if int(user_input) == 0:
                return

            if int(user_input) == 1:
                # Inform the user about what stops are currently in the database. QueryDB executes a SQLite query.
                stop_dict = QueryDB.get_scraped_stops()
                print('Currently you have these stops in your database:\n')
                for key, value in stop_dict.items():
                    print("STOP_ID: {:5d} (ROUTE: {:s})".format(key, value))

            if int(user_input) == 2:
                stop_choice = input("Select which stops you'd like to delete data for (for multiple stops separate by "
                                   "commas, e.g. 8864, 8894, 8809\n")
                print(f'Deleting all data for {stop_choice}')
                # Process the user input. If they entered comma-separated values, this block is triggered, which cleans
                # up the input.
                if ',' in stop_choice:
                    stops_to_delete = stop_choice.split(',')
                    for i in range(len(stops_to_delete)):
                        stops_to_delete[i] = stops_to_delete[i].strip()

                # If one stop was entered, strip off the white space and wrap it in a list.
                if ',' not in stop_choice:
                    stops_to_delete = [stop_choice.strip()]

                # Pass the list of stops to delete_by_criteria, which deletes all data points matching those routes.
                DeleteDBRecords.delete_by_stops(stops_to_delete)

                print(f'Successfully deleted all data for {stop_choice}')

    # If the user selected the option to delete all data from specific routes, this function is called.
    @staticmethod
    def __delete_by_routes():
        while True:
            user_input = input(
                "***Delete By ROUTE_ID***\n0) Return to Delete Menu.\n1) See all routes in your database.\n"
                "2) Enter IDs and delete data.\n")

            if not user_input.isdigit():
                print("\nPlease enter an integer to select one of the menu options.\n")

            if int(user_input) == 0:
                return

            if int(user_input) == 1:
                # Inform the user about what stops are currently in the database. QueryDB executes a SQLite query.
                print('Currently you have these routes in your database:\n')
                routes = QueryDB.get_scraped_routes()
                for route in routes:
                    print(f"Route ID: {route[0]}")

            if int(user_input) == 2:
                route_choice = input("Select which routes you'd like to delete data for separated by commas, for "
                                   "example: 71A, 71C\n")

                print(f'Deleting all data for {user_input}')

                # Process the user input. If they entered comma-separated values, this block is triggered, which cleans up the
                # input.
                if ',' in route_choice:
                    routes_to_delete = route_choice.split(',')
                    for i in range(len(routes_to_delete)):
                        routes_to_delete[i] = routes_to_delete[i].strip().upper()

                # If one route was entered, strip off the white space and wrap it in a list.
                if ',' not in route_choice:
                    routes_to_delete = [route_choice.strip().upper()]

                # Pass the list of routes to delete_by_criteria, which deletes all data points matching those routes.
                DeleteDBRecords.delete_by_lines(routes_to_delete)

                print(f'Successfully deleted all data for {route_choice}')

    # If the user selected the option to delete all data from specific dates, this function is called.
    @staticmethod
    def __delete_by_dates():
        while True:
            user_input = input(
                "***Delete By Date***\n0) Return to Delete Menu.\n1) See all dates represented in your database.\n"
                "2) Enter dates and delete data.\n")

            if not user_input.isdigit():
                print("\nPlease enter an integer to select one of the menu options.\n")

            if int(user_input) == 0:
                return

            if int(user_input) == 1:
                print('Currently you have data from these days in your database:')
                # Inform the user about what dates are currently in the database. QueryDB executes a SQLite query.
                days = QueryDB.get_scraped_days()
                for day in days:
                    print(day)
                print("\n")

            if int(user_input) == 2:
                date_choice = input("Enter the dates you'd like to delete data for, separated by commas (e.g. "
                                    "2020-10-05, 2020-10-07)\n")

                # Process the user input. If they entered comma-separated values, this block is triggered, which cleans
                # up the input.
                valid_input = True
                if ',' in date_choice:
                    dates_to_delete = date_choice.split(',')
                    for i in range(len(dates_to_delete)):
                        dates_to_delete[i] = dates_to_delete[i].strip()
                        if len(dates_to_delete[i]) != 10:
                            print("Invalid date format entered. Please enter dates formatted like this: 2022-01-01")
                            valid_input = False

                # If one date was entered, strip off the white space and wrap it in a list.
                if ',' not in date_choice:
                    dates_to_delete = [date_choice.strip()]
                    if len(dates_to_delete[0]) != 10:
                        print("Invalid date format entered. Please enter dates formatted like this: 2022-01-01")
                        valid_input = False

                if valid_input:
                    print(f'Deleting all data for {date_choice}')
                    # Pass the list of dates to delete_by_criteria, which deletes all data points matching those dates.
                    DeleteDBRecords.delete_by_dates(dates_to_delete)

                    print(f'Successfully deleted all data for {date_choice}')

    @staticmethod
    def delete_window():
        while True:
            # Get the list of all tuples in the ESTIMATES table.
            n_records = QueryDB.count_estimates()[0][0]

            user_input = input(f"\n***Delete Data from Local Database\nYou currently have {n_records} scraped ETA data "
                               "points in your database.\n0) Return to Main Menu.\n1) Delete all scraped data.\n"
                               "2) Delete by stop ID.\n3) Delete by route ID.\n4) Delete by dates.\n")

            if not user_input.isdigit():
                print("\nPlease enter an integer to select one of the menu options.\n")

            if int(user_input) == 0:
                return

            # If the user selects DELETE ALL, drop all existing tables and scape an updated list of stop names and route
            # names from the TrueTime website, which will be the basis of any future scraping.
            if int(user_input) == 1:
                print("Deleting all scraped ETA data points. Scraping the TrueTime website to find an updated set of "
                      "stops and routes...\n")
                CreateDB.drop_estimates()
                print("Deletion complete.\n")

            # These three functions provide a similar feature, which allows the user to delete all ESTIMATES tuples
            # matching stops, routes, or dates respectively.
            if int(user_input) == 2:
                DeleteInterface.__delete_by_stops()

            if int(user_input) == 3:
                DeleteInterface.__delete_by_routes()

            if int(user_input) == 4:
                DeleteInterface.__delete_by_dates()
