import os
import sqlite3
import unittest
from astropy.time import Time, TimeDelta
from lsst.utils import getPackageDir
import lsst.utils.tests
from lsst.utils.tests import getTempFilePath

from lsst.sims.cloudModel import CloudData

class TestCloudModel(unittest.TestCase):

    def setUp(self):
        self.th = Time('2020-01-01', format='isot', scale='tai')
        self.cloud_db = os.path.join(getPackageDir('sims_cloudModel'), 'data', 'cloud.db')
        self.num_original_values = 29201

    def test_basic_information_after_creation(self):
        cloudData = CloudData(self.th, cloud_db=self.cloud_db)
        self.assertIsNone(cloudData.cloud_dates)
        self.assertIsNone(cloudData.cloud_values)
        self.assertEqual(cloudData.start_time, self.th)
        cloudData = CloudData(self.th, cloud_db=self.cloud_db, offset_year = 1)
        self.assertEqual(cloudData.start_time, Time('2021-01-01', format='isot', scale='tai'))

    def test_information_after_initialization(self):
        # Test setting cloud_db explicitly.
        cloudData = CloudData(self.th, cloud_db=self.cloud_db)
        cloudData.read_data()
        self.assertEqual(cloudData.cloud_values.size, self.num_original_values)
        self.assertEqual(cloudData.cloud_dates.size, self.num_original_values)
        # Test that find built-in module automatically.
        cloudData = CloudData(self.th)
        cloudData.read_data()
        self.assertEqual(cloudData.cloud_dates.size, self.num_original_values)

    def test_get_clouds(self):
        cloudData = CloudData(self.th, cloud_db=self.cloud_db)
        cloudData.read_data()
        dt = TimeDelta(700000, format='sec')
        self.assertEqual(cloudData(self.th + dt), 0.5)
        dt = TimeDelta(701500, format='sec')
        self.assertEqual(cloudData(self.th + dt), 0.5)
        dt = TimeDelta(705000, format='sec')
        self.assertEqual(cloudData(self.th + dt), 0.375)
        dt = TimeDelta(630684000, format='sec')
        self.assertEqual(cloudData(self.th + dt), 0.0)

    def test_get_clouds_using_different_start_month(self):
        # Just changing the starting month
        t2 = Time('2020-05-24', format='isot', scale='tai')
        cloud1 = CloudData(t2)
        self.assertEqual(cloud1.start_time, self.th)
        cloud1.read_data()
        dt = TimeDelta(700000, format='sec')
        self.assertEqual(cloud1(t2 + dt), 0.0)
        dt = TimeDelta(630684000, format='sec')
        self.assertEqual(cloud1(t2 + dt), 0.25)

    def test_alternate_db(self):
        with getTempFilePath('.alt_cloud.db') as tmpdb:
            cloud_dbfile = tmpdb
            cloud_table = []
            cloud_table.append("cloudId INTEGER PRIMARY KEY")
            cloud_table.append("c_date INTEGER")
            cloud_table.append("cloud DOUBLE")
            with sqlite3.connect(cloud_dbfile) as conn:
                cur = conn.cursor()
                cur.execute("DROP TABLE IF EXISTS Cloud")
                cur.execute("CREATE TABLE Cloud({})".format(",".join(cloud_table)))
                cur.executemany("INSERT INTO Cloud VALUES(?, ?, ?)", [(1, 9997, 0.5), (2, 10342, 0.125)])
                cur.close()
            cloud1 = CloudData(self.th, tmpdb)
            cloud1.read_data()
            self.assertEqual(cloud1.cloud_values.size, 2)
            self.assertEqual(cloud1.cloud_values[1], 0.125)

class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass

def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
