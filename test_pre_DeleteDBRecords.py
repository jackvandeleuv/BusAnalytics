import unittest
import sqlite3


# This unittest checks whether the DeleteDBRecords class is deleting data correctly. This test only works with the
# 27,791,360 byte version of the test database, which has a known output.
class TestAvgWaitTimeGenerator(unittest.TestCase):

    # Check that there is the correct number records in the database under each category before we try to delete
    # anything.
    def test_records_in_db_by_dates(self):
        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()
        cur.execute("SELECT COUNT(ID) FROM ESTIMATES WHERE SUBSTR(TIME_CHECKED, 1, 10) IN ('2022-10-08','1010-10-10')")
        count_before = cur.fetchall()
        count_before = count_before[0][0]
        connection.commit()
        self.assertEqual(41880, count_before)

    def test_records_in_db_by_stops(self):
        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()
        cur.execute("SELECT COUNT(ID) FROM ESTIMATES WHERE STOP_ID IN (8280, 38, 8805)")
        count_before = cur.fetchall()
        count_before = count_before[0][0]
        connection.commit()
        self.assertEqual(3598, count_before)

    def test_records_in_db_by_routes(self):
        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()
        cur.execute("SELECT COUNT(ID) FROM ESTIMATES WHERE ROUTE_ID IN ('71A', '71C')")
        count_before = cur.fetchall()
        count_before = count_before[0][0]
        connection.commit()
        self.assertEqual(265766, count_before)
