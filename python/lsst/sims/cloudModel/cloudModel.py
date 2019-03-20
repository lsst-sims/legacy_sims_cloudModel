from builtins import object
from collections import OrderedDict
import numpy as np
from .cloudModelConfig import CloudModelConfig
from lsst.sims.cloudModel import version


__all__ = ["CloudModel"]


class CloudModel(object):
    """LSST cloud calculations for cloud extinction.
    Currently this actually only returns the cloud coverage of the sky, exactly as reported in the
    cloud database (thus the sky coverage, in fractions of 8ths).


    Parameters
    ----------
    config: CloudModelConfig, opt
        A configuration class for the cloud model.
        This can be None, in which case the default CloudModelConfig is used.
        The user should set any non-default values for CloudModelConfig before
        configuration of the actual CloudModel.

    self.efd_requirements and self.map_requirements are also set.
    efd_requirements is a tuple: (list of str, float).
    This corresponds to the data columns required from the EFD and the amount of time history required.
    target_requirements is a list of str.
    This corresponds to the data columns required in the target map dictionary passed when calculating the
    processed telemetry values.
    """
    def __init__ (self, config=None):
        self._configure(config=config)
        self.efd_requirements = (self._config.efd_columns, self._config.efd_delta_time)
        self.target_requirements = self._config.target_columns
        self.altcol = self.target_requirements[0]
        self.azcol = self.target_requirements[1]
        self.efd_cloud = self._config.efd_columns[0]

    def _configure(self, config=None):
        """Configure the model. After 'configure' the model config will be frozen.

        Parameters
        ----------
        config: CloudModelConfig, opt
            A configuration class for the cloud model.
            This can be None, in which case the default values are used.
        """
        if config is None:
            self._config = CloudModelConfig()
        else:
            if not isinstance(config, CloudModelConfig):
                raise ValueError('Must use a CloudModelConfig.')
            self._config = config
        self._config.validate()
        self._config.freeze()

    def config_info(self):
        """Report configuration parameters and version information.

        Returns
        -------
        OrderedDict
        """
        config_info = OrderedDict()
        config_info['CloudModel_version'] = '%s' % version.__version__
        config_info['CloudModel_sha'] = '%s' % version.__fingerprint__
        for k, v in self._config.iteritems():
            config_info[k] = v
        return config_info

    def __call__(self, efdData, targetDict):
        """Calculate the sky coverage due to clouds.

        This is where we'd plug in Peter's cloud transparency maps and predictions.
        We could also try translating cloud transparency into a cloud extinction.
        For now, we're simply returning the cloud coverage that we already got from the database,
        but multiplied over the whole sky to provide a map.

        Parameters
        ----------
        efdData: dict
            Dictionary of input telemetry, typically from the EFD.
            This must contain columns self.efd_requirements.
            (work in progress on handling time history).
        targetDict: dict
            Dictionary of target map values over which to calculate the processed telemetry.
            (e.g. targetDict = {'ra': [], 'dec': [], 'altitude': [], 'azimuth': [], 'airmass': []})
            Here we use 'altitude' and 'azimuth', which should be numpy arrays .

        Returns
        -------
        dict of np.ndarray
            Cloud transparency map values.
        """
        model_cloud = np.zeros(len(targetDict[self.altcol]), float) + efdData[self.efd_cloud]
        return {'cloud': model_cloud}