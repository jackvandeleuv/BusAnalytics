import unittest
import sqlite3
from DeleteDBRecords import DeleteDBRecords


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# You will need a fresh copy of the test database after using this unittest!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# This unittest checks whether the DeleteDBRecords class is deleting data correctly. This test only works with the
# 27,791,360 byte version of the test database, which has a known output.
class TestAvgWaitTimeGenerator(unittest.TestCase):

    # The companion unittests called TestPreDeleteDBRecords already confirmed that the correct data is in our tables.
    # Now, we delete by three different criteria, and then check that all data in matching those criteria has been
    # deleted.
    def test_deleting_by_dates(self):
        DeleteDBRecords.delete_by_dates([('2022-10-08',), ('1010-10-10',)])
        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()
        cur.execute("SELECT COUNT(ID) FROM ESTIMATES WHERE SUBSTR(TIME_CHECKED, 1, 10) IN ('2022-10-08','1010-10-10')")
        count_before = cur.fetchall()
        count_before = count_before[0][0]
        connection.commit()
        self.assertEqual(0, count_before)

    def test_deleting_by_stops(self):
        DeleteDBRecords.delete_by_stops([('8280',), ('38',), ('8805',)])
        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()
        cur.execute("SELECT COUNT(ID) FROM ESTIMATES WHERE STOP_ID IN (8280, 38, 8805)")
        count_before = cur.fetchall()
        count_before = count_before[0][0]
        connection.commit()
        self.assertEqual(0, count_before)

    def test_deleting_by_lines(self):
        DeleteDBRecords.delete_by_lines([('71A',), ('71C',)])
        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()
        cur.execute("SELECT COUNT(ID) FROM ESTIMATES WHERE ROUTE_ID IN ('71A', '71C')")
        count_before = cur.fetchall()
        count_before = count_before[0][0]
        connection.commit()
        self.assertEqual(0, count_before)
