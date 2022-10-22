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
        self.__group_stops = False
        self.__group_routes = False
        self.__group_days = False

    def set_stop_filters(self, stops):
        assert type(stops) == list
        self.__stop_filters = stops

    def set_route_filters(self, routes):
        assert type(routes) == list
        self.__route_filters = routes

    def set_day_filters(self, days):
        assert type(days) == list
        self.__day_filters = days

    def set_stop_group(self, boolean):
        self.__group_stops = boolean

    def set_route_group(self, boolean):
        self.__group_routes = boolean

    def set_day_group(self, boolean):
        self.__group_days = boolean

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
            where_clause = "WHERE" + subclauses[0]

        if len(subclauses) > 1:
            subclauses = "AND".join(subclauses)
            where_clause = "WHERE" + subclauses

        return where_clause

    def make_group_clause(self):
        group_clause = ""
        subclauses = []

        if self.__group_stops:
            stop_g = "STOP_ID"
            subclauses.append(stop_g)

        if self.__group_routes:
            route_g = "ROUTE_ID"
            subclauses.append(route_g)

        if self.__group_days:
            day_g = "SUBSTR(TIME_CHECKED, 1, 10)"
            subclauses.append(day_g)

        if len(subclauses) != 0:
            subclauses = ", ".join(subclauses)
            group_clause = "GROUP BY " + subclauses

        print(group_clause)

    def get_scrape_ids(self, cur):
        cur.execute("SELECT DISTINCT(SCRAPE_ID) FROM ESTIMATES")
        scrape_ids = cur.fetchall()
        return scrape_ids

    def calc_zeros(self, cur, scrape_id):
        cur.execute("""
                    SELECT STOP_ID, MAX(TIME_CHECKED), MIN(ETA), ROUTE_ID
                    FROM ESTIMATES
                    WHERE SCRAPE_ID = ? 
                    GROUP BY SCRAPE_ID, ROUTE_ID, STOP_ID, VEHICLE_ID
                    """, scrape_id)
        results = cur.fetchall()

        zeros_dict = {}
        for row in results:
            stop_id = row[0]
            max_stamp = row[1]
            eta = row[2]
            route_id = row[3]
            arrival = inner_dt.fromisoformat(max_stamp) + datetime.timedelta(minutes=eta)

            stop_in_row = (stop_id, route_id) in zeros_dict
            if stop_in_row:
                temp_list = zeros_dict[(stop_id, route_id)]
                temp_list.append(arrival)
            if not stop_in_row:
                zeros_dict[(stop_id, route_id)] = [arrival]

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

    def calc_gaps(self):
        conn = sqlite3.Connection("transit_data.db")
        cur = conn.cursor()

        scrape_ids = self.get_scrape_ids(cur)
        gaps_by_stop = {}
        for scrape_id in scrape_ids:
            zeros_dict = self.calc_zeros(cur, scrape_id)
            for key, value in zeros_dict.items():
                key_in_gaps_dict = key in gaps_by_stop
                if not key_in_gaps_dict:
                    gaps_by_stop[key] = self.zeros_to_gaps(value)
                if key_in_gaps_dict:
                    gaps_by_stop[key].extend(self.zeros_to_gaps(value))

        conn.commit()
        return gaps_by_stop

    def query_test(self):
        conn = sqlite3.Connection("transit_data.db")
        cur = conn.cursor()

        cur.execute("""
        SELECT *
        FROM ESTIMATES
        WHERE STOP_ID = 8192
        """)
        results = cur.fetchall()
        for r in results:
            print(r)

        # cur.execute("SELECT * FROM ESTIMATES WHERE VEHICLE_ID = 5810 AND SCRAPE_ID = 1665243291.0")
        # results = cur.fetchall()
        # for r in results:
        #     print(r)
        # conn.commit()


sg = StatsGenerator()
gaps_by_stops = sg.calc_gaps()
for key, value in gaps_by_stops.items():
    total = 0
    for v in value:
        if key == 8192:
            print(v)
        total += v
    if total != 0:
        print(key, ":", total / (len(value) * 60))



# sg.query_test()
