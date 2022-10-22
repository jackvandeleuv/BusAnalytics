import copy
import sqlite3
import timeit
from datetime import datetime as inner_dt
import datetime
import time


class StatsGenerator:
    def __init__(self):
        self.__stop_filters = []
        self.__route_filters = []
        self.__day_filters = []

    def set_stop_filters(self, newStops):
        assert type(newStops) == list
        stops = copy.deepcopy(newStops)
        self.__stop_filters = stops

    def set_route_filters(self, newRoutes):
        assert type(newRoutes) == list
        routes = copy.deepcopy(newRoutes)
        self.__route_filters = routes

    def set_day_filters(self, newDays):
        assert type(newDays) == list
        days = copy.deepcopy(newDays)
        self.__day_filters = days

    def print_filters(self):
        print(f"Your current filters are:\nSTOP_IDS: {self.__stop_filters}\nROUTE_IDS: {self.__route_filters}\n"
              f"DAYS: {self.__day_filters}\n")

    def __make_where_clause(self):
        where_clause = ""
        subclauses = []

        if len(self.__stop_filters) != 0:
            stop_in = " STOP_ID IN ("
            for i in range(len(self.__stop_filters)):
                stop_in = stop_in + "?,"
            stop_in = stop_in[:-1] + ") "
            subclauses.append(stop_in)

        if len(self.__route_filters) != 0:
            route_in = " ROUTE_ID IN ("
            for i in range(len(self.__route_filters)):
                route_in = route_in + "?,"
            route_in = route_in[:-1] + ") "
            subclauses.append(route_in)

        if len(self.__day_filters) != 0:
            days_in = " SUBSTR(TIME_CHECKED, 1, 10) IN ("
            for i in range(len(self.__day_filters)):
                days_in = days_in + "?,"
            days_in = days_in[:-1] + ") "
            subclauses.append(days_in)

        if len(subclauses) == 1:
            where_clause = "AND " + subclauses[0]

        if len(subclauses) > 1:
            where_clause = "AND".join(subclauses)
            where_clause = "AND " + where_clause

        return where_clause

    def get_scrape_ids(self, cur):
        cur.execute("SELECT DISTINCT(SCRAPE_ID) FROM ESTIMATES")
        scrape_ids = cur.fetchall()
        return scrape_ids

    def calc_zeros(self, cur, scrape_id, both_bool):
        query = """SELECT STOP_ID, MAX(TIME_CHECKED), MIN(ETA), ROUTE_ID
                    FROM ESTIMATES 
                    WHERE SCRAPE_ID = ? """

        query = query + self.__make_where_clause()
        query = query + "GROUP BY SCRAPE_ID, STOP_ID, VEHICLE_ID "
        if both_bool:
            query = query + ", ROUTE_ID"

        params = [scrape_id]
        if len(self.__stop_filters) != 0:
            params.extend(self.__stop_filters)
        if len(self.__route_filters) != 0:
            params.extend(self.__route_filters)
        if len(self.__day_filters) != 0:
            params.extend(self.__day_filters)

        cur.execute(query, tuple(params))
        results = cur.fetchall()

        zeros_dict = {}
        for row in results:
            stop_id = row[0]
            max_stamp = row[1]
            eta = row[2]
            route_id = row[3]
            arrival = inner_dt.fromisoformat(max_stamp) + datetime.timedelta(minutes=eta)

            if both_bool:
                zeros_key = (stop_id, route_id)
            if not both_bool:
                zeros_key = stop_id

            stop_in_row = zeros_key in zeros_dict
            if stop_in_row:
                temp_list = zeros_dict[zeros_key]
                temp_list.append(arrival)
            if not stop_in_row:
                zeros_dict[zeros_key] = [arrival]

        return zeros_dict

    def zeros_to_gaps(self, zeros_list):
        zeros_list.sort(reverse=True)
        gaps_list = []
        for i in range(len(zeros_list) - 1):
            older_zero = zeros_list[i]
            newer_zero = zeros_list[i + 1]
            delta = older_zero - newer_zero
            delta_secs = delta.total_seconds()
            gaps_list.append(delta_secs)
        return gaps_list

    def calc_gaps(self, both_bool):
        conn = sqlite3.Connection("transit_data.db")
        cur = conn.cursor()

        scrape_ids = self.get_scrape_ids(cur)
        gaps_dict = {}
        for scrape_id in scrape_ids:
            zeros_dict = self.calc_zeros(cur, scrape_id[0], both_bool)
            for key, value in zeros_dict.items():
                key_in_gaps_dict = key in gaps_dict
                if not key_in_gaps_dict:
                    gaps_dict[key] = self.zeros_to_gaps(value)
                if key_in_gaps_dict:
                    gaps_dict[key].extend(self.zeros_to_gaps(value))

        conn.commit()
        return gaps_dict

    def group_by_both(self):
        print("Calculating frequency...\n")
        gaps_dict = self.calc_gaps(True)
        for key, value in gaps_dict.items():
            if len(value):
                print("STOP_ID: {:5d}, ROUTE_ID: {:>3s}, AVG FREQUENCY: EVERY {:4.3f} MINS".format(
                    key[0], str(key[1]), sum(value) / (len(value) * 60)
                ))
            if not len(value):
                print("STOP_ID: {:5d}, ROUTE_ID: {:>3s}, AVG FREQUENCY: NOT FOUND".format(
                    key[0], str(key[1])))

    def group_by_stop(self):
        print("Calculating frequency...\n")
        gaps_dict = self.calc_gaps(False)
        for key, value in gaps_dict.items():
            if len(value):
                print("STOP_ID: {:5d}, AVG FREQUENCY: EVERY {:4.3f} MINS".format(
                    key, sum(value) / (len(value) * 60)
                ))
            if not len(value):
                print("STOP_ID: {:5d}, AVG FREQUENCY: NOT FOUND".format(
                    key))

    def overall_frequency(self):
        print("Calculating frequency...\n")
        gaps_dict = self.calc_gaps(False)
        all_gaps = []
        for value in gaps_dict.values():
            all_gaps.extend(value)
        if len(all_gaps):
            print("OVERALL AVG FREQUENCY: EVERY {:4.3f} MINS\n".format(
                sum(all_gaps) / (len(all_gaps) * 60)))
        if not len(all_gaps):
            print("OVERALL AVG FREQUENCY: NO DATA FOUND USING CURRENT FILTERS")
