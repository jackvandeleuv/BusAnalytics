import copy
import sqlite3
from datetime import datetime as inner_dt
import datetime


# This class provides methods that allow the ScrapeInterface window to calculate summary statistics for our dataset.
# The class includes instance variables, which are user-defined filters that persist over the course of a single user.
# session.
class StatsGenerator:
    def __init__(self):
        # These three instance variables specify different filters to apply to our dataset.
        # STOP_IDs to filter by.
        self.__stop_filters = []
        # ROUTE_IDs to filter by.
        self.__route_filters = []
        # Dates to filter by. These dates represented days on which scraped data was collected.
        self.__day_filters = []

    # Setter for stop filters.
    def set_stop_filters(self, newStops):
        # Validate input, which should be a list.
        assert type(newStops) == list
        # Make a defensive copy to preserve encapsulation.
        stops = copy.deepcopy(newStops)
        self.__stop_filters = stops

    # Setter for route filters.
    def set_route_filters(self, newRoutes):
        # Validate input, which should be a list.
        assert type(newRoutes) == list
        # Make a defensive copy to preserve encapsulation.
        routes = copy.deepcopy(newRoutes)
        self.__route_filters = routes

    # Setter for day filters.
    def set_day_filters(self, newDays):
        # Validate input, which should be a list.
        assert type(newDays) == list
        # Make a defensive copy to preserve encapsulation.
        days = copy.deepcopy(newDays)
        self.__day_filters = days

    # Print a formatted list of all filters currently chosen by the user.
    def print_filters(self):
        print(f"Your current filters are:\nSTOP_IDS: {self.__stop_filters}\nROUTE_IDS: {self.__route_filters}\n"
              f"DAYS: {self.__day_filters}\n")

    # This function creates a SQLite WHERE clause with variable numbers of parameter placeholders depending on the
    # number of filters specified in the instance variables of this object.
    def __make_where_clause(self):
        where_clause = ""
        subclauses = []

        # If there are currently any stop filters, construct a string formatted similar to STOP_ID IN (?, ?, ?)
        if len(self.__stop_filters) != 0:
            stop_in = " STOP_ID IN ("
            for i in range(len(self.__stop_filters)):
                stop_in = stop_in + "?,"
            stop_in = stop_in[:-1] + ") "
            # Add the subclass to a list with other subclauses, if any.
            subclauses.append(stop_in)

        # If there are currently any route filters, construct a string formatted similar to ROUTE_ID IN (?, ?)
        if len(self.__route_filters) != 0:
            route_in = " ROUTE_ID IN ("
            for i in range(len(self.__route_filters)):
                route_in = route_in + "?,"
            route_in = route_in[:-1] + ") "
            # Add the subclass to a list with other subclauses, if any.
            subclauses.append(route_in)

        # If there are any date filters, generate a sub-clause that pulls out a slice of each ISO-formatted date string
        # in the transit_data.db database. The slice will be formatted like YYYY-MM-DD.
        if len(self.__day_filters) != 0:
            days_in = " SUBSTR(TIME_CHECKED, 1, 10) IN ("
            for i in range(len(self.__day_filters)):
                days_in = days_in + "?,"
            days_in = days_in[:-1] + ") "
            # Add the subclass to a list with other subclauses, if any.
            subclauses.append(days_in)

        # If only one sub-clause was required, package it together with AND to fit the larger query.
        if len(subclauses) == 1:
            where_clause = "AND " + subclauses[0]

        # If multiple sub-clauses are required, join them on AND and add an AND to the front to fit the larger query.
        if len(subclauses) > 1:
            where_clause = "AND".join(subclauses)
            where_clause = "AND " + where_clause

        # If no sub-clauses were required, an empty string is returned as the WHERE clause.
        return where_clause

    # Get a list of all distinct SCRAPE_IDs represented in the database.
    def get_scrape_ids(self, cur):
        cur.execute("SELECT DISTINCT(SCRAPE_ID) FROM ESTIMATES")
        scrape_ids = cur.fetchall()
        return scrape_ids

    # The calc_zeros function returns a dict with STOP_IDs as keys and lists as values. Each list contains some datetime
    # objects, each of which represent a time when a bus arrived at the given stop.
    #   Arguments: "group_by_route" is a user-selected option, indicating whether the user wants to group results by
    #   routes and stops, or only by stops. Cur is a cursor object with which the function can query the database.
    def calc_zeros(self, cur, scrape_id, group_by_route):
        # This block concatenates a query string together, which receives a parameterized input.
        query = """SELECT STOP_ID, MAX(TIME_CHECKED), MIN(ETA), ROUTE_ID
                    FROM ESTIMATES 
                    WHERE SCRAPE_ID = ? """
        # __make_where_clause() checks for user-defined filters, and constructs an appropriate sub-clause if so.
        query = query + self.__make_where_clause()
        query = query + "GROUP BY SCRAPE_ID, STOP_ID, VEHICLE_ID "
        # If the user wishes to group by route (in addition to stop), add this additional GROUP BY sub-clause to the
        # end of this line.
        if group_by_route:
            query = query + ", ROUTE_ID"

        # At a minimum, the query will take scrape_id as a parameter. The parameter list is extended as necessary if
        # additional parameters exist in any of the three filter lists stored as instance variables.
        params = [scrape_id]
        if len(self.__stop_filters) != 0:
            params.extend(self.__stop_filters)
        if len(self.__route_filters) != 0:
            params.extend(self.__route_filters)
        if len(self.__day_filters) != 0:
            params.extend(self.__day_filters)

        # Cast the list to a tuple as required by SQLite3.
        cur.execute(query, tuple(params))
        results = cur.fetchall()

        # Create a dict. The keys will either be stop_ids or two-tuples with stop_ids and route_ids packaged together.
        # The values will be lists of datetime objects, which each object representing a time when a bus arrived at the
        # stop.
        zeros_dict = {}
        for row in results:
            # Store each item from the SQL query in a variable.
            stop_id = row[0]
            max_stamp = row[1]
            eta = row[2]
            route_id = row[3]

            # The "zero", i.e. the time when a bus arrived at a stop, is stored in the arrival variable. In order to
            # find this "zero" timestamp, we take the last timestamp downloaded from the TrueTime website and add to it
            # a time delta equal to the number of minutes represented by the lowest ETA.
            #
            # This works because our query groups together results by stop and vehicle_id, and identifies breaks in the
            # data using the scrape_id attribute. Thus, every row returned by the query represents the last time a
            # particular incoming vehicle was identified and scraped. If the ETA reported by the TrueTime website was
            # not 0, we assume the ETA was correct and add the remaining minutes to the time stamp.
            arrival = inner_dt.fromisoformat(max_stamp) + datetime.timedelta(minutes=eta)

            # Define zeros_key differently depending on whether the user selected the group by route option.
            if group_by_route:
                zeros_key = (stop_id, route_id)
            if not group_by_route:
                zeros_key = stop_id

            # Check if the stop already has elements in its list.
            stop_in_row = zeros_key in zeros_dict
            if stop_in_row:
                # Add the new arrival timestamp to the dictionary.
                temp_list = zeros_dict[zeros_key]
                temp_list.append(arrival)
            if not stop_in_row:
                zeros_dict[zeros_key] = [arrival]

        return zeros_dict

    # This method calculates the gaps between the timestamps, each of which is a "zero," i.e. a time when the ETA of a
    # bus at a particular stop was 0 minutes. Because this list is processed separately for each scrape_id, it does not
    # need to worry about gaps between scraping sessions.
    def zeros_to_gaps(self, zeros_list):
        # Sort the list of datetime objects so that they are in chronological order.
        zeros_list.sort(reverse=True)
        gaps_list = []
        for i in range(len(zeros_list) - 1):
            older_zero = zeros_list[i]
            newer_zero = zeros_list[i + 1]
            # The delta is a timedelta object, which identifies the gap between two time stamps.
            delta = older_zero - newer_zero
            # Convert the delta to seconds.
            delta_secs = delta.total_seconds()
            gaps_list.append(delta_secs)
        return gaps_list

    # This function generates a list of floats, each representing a gap between two bus arrivals at a stop (in seconds).
    # group_by_route is a bool, which is selected by the user. If it is True, this indicates that we should calculate
    # gaps between arrivals on a particular bus line (as opposed to gaps between arrivals of any type of bus at the
    # stop).
    def calc_gaps(self, group_by_route):
        conn = sqlite3.Connection("transit_data.db")
        cur = conn.cursor()

        # Get list of all scrape_ids stored it our database.
        scrape_ids = self.get_scrape_ids(cur)
        gaps_dict = {}
        for scrape_id in scrape_ids:
            # Each scrape_id was returned by an SQLite query as a one-tuple, so we specify scrape_id[0].
            zeros_dict = self.calc_zeros(cur, scrape_id[0], group_by_route)
            for key, value in zeros_dict.items():
                key_in_gaps_dict = key in gaps_dict
                # Once each list of arrival timestamps has been converted to "gaps," i.e. time between arrivals in
                # seconds, we can store the gaps from different scrape ids together.
                if not key_in_gaps_dict:
                    gaps_dict[key] = self.zeros_to_gaps(value)
                if key_in_gaps_dict:
                    gaps_dict[key].extend(self.zeros_to_gaps(value))

        conn.commit()
        return gaps_dict

    # This function is called if the user asks for average frequency broken out by both stop and route.
    def group_by_both(self):
        print("Calculating frequency...\n")
        # The keys of this dict are two-tuples containing a stop_id and route_id. The values are a list of floats,
        # each representing a gap between two bus arrivals at a stop.
        gaps_dict = self.calc_gaps(True)
        for key, value in gaps_dict.items():
            if len(value):
                # For each key, average the list of floats into a single average number.
                print("STOP_ID: {:5d}, ROUTE_ID: {:>3s}, AVG FREQUENCY: EVERY {:4.3f} MINS".format(
                    key[0], str(key[1]), sum(value) / (len(value) * 60)
                ))
            # If the value of an element in the dict is empty, that means no data was able to be calculated for that
            # element.
            if not len(value):
                print("STOP_ID: {:5d}, ROUTE_ID: {:>3s}, AVG FREQUENCY: NOT FOUND".format(
                    key[0], str(key[1])))

    # This function is called if the user asks for average frequency broken out by stop only.
    def group_by_stop(self):
        print("Calculating frequency...\n")
        # The keys of this dict are stop_id strings. The values are a list of floats, each representing a gap between
        # two bus arrivals at a stop.
        gaps_dict = self.calc_gaps(False)
        for key, value in gaps_dict.items():
            if len(value):
                # For each key, average the list of floats into a single average number.
                print("STOP_ID: {:5d}, AVG FREQUENCY: EVERY {:4.3f} MINS".format(
                    key, sum(value) / (len(value) * 60)
                ))
            # If the value of an element in the dict is empty, that means no data was able to be calculated for that
            if not len(value):
                print("STOP_ID: {:5d}, AVG FREQUENCY: NOT FOUND".format(
                    key))

    # This function calculates the average gap between bus arrivals for all stops and routes in the database.
    def overall_frequency(self):
        print("Calculating frequency...\n")
        gaps_dict = self.calc_gaps(False)
        all_gaps = []
        # Combine every gap identified in the bus system into a single list.
        for value in gaps_dict.values():
            all_gaps.extend(value)
        if len(all_gaps):
            # Average the all_gaps list to find the average frequency across every scraped stop.
            print("OVERALL AVG FREQUENCY: EVERY {:4.3f} MINS\n".format(
                sum(all_gaps) / (len(all_gaps) * 60)))
        if not len(all_gaps):
            print("OVERALL AVG FREQUENCY: NO DATA FOUND USING CURRENT FILTERS")
