import os
import sqlite3
import unittest
from lsst.utils import getPackageDir
import lsst.utils.tests
from lsst.utils.tests import getTempFilePath

from lsst.sims.cloudModel import CloudModel
from lsst.sims.utils import TimeHandler

class TestCloudModel(unittest.TestCase):

    def setUp(self):
        self.th = TimeHandler("2020-01-01")
        self.cloud_db = os.path.join(getPackageDir('sims_cloudModel'), 'data', 'cloud.db')
        self.cloud = CloudModel(self.th)
        self.num_original_values = 29201

    def test_basic_information_after_creation(self):
        cloud = CloudModel(self.th)
        self.assertIsNone(cloud.cloud_db)
        self.assertIsNone(cloud.cloud_dates)
        self.assertIsNone(cloud.cloud_values)
        self.assertEqual(cloud.offset, 0)

    def test_information_after_initialization(self):
        # Test setting cloud_db explicitly.
        self.cloud.read_data(self.cloud_db)
        self.assertEqual(self.cloud.cloud_values.size, self.num_original_values)
        self.assertEqual(self.cloud.cloud_dates.size, self.num_original_values)
        # Test that find built-in module.
        cloud = CloudModel(self.th)
        cloud.read_data()
        self.assertEqual(self.cloud.cloud_dates.size, self.num_original_values)

    def test_get_clouds(self):
        self.cloud.read_data(self.cloud_db)
        self.assertEqual(self.cloud.get_cloud(700000), 0.5)
        self.assertEqual(self.cloud.get_cloud(701500), 0.5)
        self.assertEqual(self.cloud.get_cloud(705000), 0.375)
        self.assertEqual(self.cloud.get_cloud(630684000), 0.0)

    def test_get_clouds_using_different_start_month(self):
        cloud1 = CloudModel(TimeHandler("2020-05-24"))
        self.assertEqual(cloud1.offset, 12441600)
        cloud1.read_data(self.cloud_db)
        self.assertEqual(cloud1.get_cloud(700000), 0.0)
        self.assertEqual(cloud1.get_cloud(701500), 0.0)
        self.assertEqual(cloud1.get_cloud(705000), 0.0)
        self.assertEqual(cloud1.get_cloud(630684000), 0.25)

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
            cloud1 = CloudModel(TimeHandler("2020-01-01"))
            cloud1.read_data(cloud_db=tmpdb)
            self.assertEqual(cloud1.cloud_values.size, 2)
            self.assertEqual(cloud1.cloud_values[1], 0.125)

class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass

def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
