import numpy as np
import unittest
import lsst.utils.tests
from lsst.sims.cloudModel import CloudModel, CloudModelConfig


class TestCloudModel(unittest.TestCase):
    def setUp(self):
        # Set config to known values.
        config = CloudModelConfig()
        config.efd_columns = ['cloud']
        config.efd_delta_time = 30
        config.target_columns = ['altitude', 'azimuth']
        config.model_keys = ['cloud']
        self.config = config

    def test_configure(self):
        # Configure with defaults.
        cloudModel = CloudModel()
        conf = CloudModelConfig()
        self.assertEqual(cloudModel._config, conf)
        # Test specifying the config.
        cloudModel = CloudModel(self.config)
        self.assertEqual(cloudModel._config.efd_delta_time, self.config.efd_delta_time)
        # Test specifying an incorrect config.
        self.assertRaises(ValueError, CloudModel, 0.8)

    def test_status(self):
        cloudModel = CloudModel()
        confDict = cloudModel.config_info()
        expected_keys = ['CloudModel_version', 'CloudModel_sha', 'efd_columns', 'efd_delta_time',
                         'target_columns', 'model_keys']
        for k in expected_keys:
            self.assertTrue(k in confDict.keys())

    def test_efd_requirements(self):
        cloudModel = CloudModel(self.config)
        cols, deltaT = cloudModel.efd_requirements
        self.assertEqual(self.config.efd_columns, cols)
        self.assertEqual(self.config.efd_delta_time, deltaT)

    def test_call(self):
        cloudModel = CloudModel(self.config)
        in_cloud = 1.53
        efdData = {'cloud': in_cloud}
        alt = np.zeros(50, float)
        az = np.zeros(50, float)
        targetDict = {'altitude': alt, 'azimuth': az}
        modelData = cloudModel(efdData, targetDict)
        for k in self.config.model_keys:
            self.assertTrue(k in modelData)
        # Test that we propagated cloud value over the whole sky.
        out_cloud = modelData['cloud']
        self.assertEqual(in_cloud, out_cloud.max())
        self.assertEqual(in_cloud, out_cloud.min())
        self.assertEqual(len(out_cloud), len(alt))


class TestMemory(lsst.utils.tests.MemoryTestCase):
    pass

def setup_module(module):
    lsst.utils.tests.init()

if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
