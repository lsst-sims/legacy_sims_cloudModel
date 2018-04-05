from builtins import object
from datetime import datetime
import os
import sqlite3
import numpy as np
from lsst.utils import getPackageDir

__all__ = ["CloudModel"]


class CloudModel(object):
    """Handle the cloud information.

    This class deals with the cloud information that was previously produced for
    OpSim version 3.

    Parameters
    ----------
    time_handler : :class:`lsst.sims.utils.TimeHandler`
        The instance of the simulation time handler.
    """
    def __init__(self, time_handler):
        self.cloud_db = None
        model_time_start = datetime(time_handler.initial_dt.year, 1, 1)
        self.offset = time_handler.time_since_given_datetime(model_time_start,
                                                             reverse=True)
        self.cloud_dates = None
        self.cloud_values = None

    def get_cloud(self, delta_time):
        """Get the cloud for the specified time.

        Parameters
        ----------
        delta_time : int
            The time (seconds) from the start of the simulation.

        Returns
        -------
        float
            The cloud (fraction of sky in 8ths) closest to the specified time.
        """
        delta_time += self.offset
        date = delta_time % self.time_range + self.min_time
        idx = np.searchsorted(self.cloud_dates, date)
        # searchsorted ensures that left < date < right
        # but we need to know if date is closer to left or to right
        left = self.cloud_dates[idx - 1]
        right = self.cloud_dates[idx]
        if date - left < right - date:
            idx -= 1
        return self.cloud_values[idx]

    def read_data(self, cloud_db=None):
        """Read the cloud data from disk.

        The default behavior is to use the module stored database. However, an
        alternate database file can be provided. The alternate database file needs to have a
        table called *Cloud* with the following columns:

        cloudId
            int : A unique index for each cloud entry.
        c_date
            int : The time (units=seconds) since the start of the simulation for the cloud observation.
        cloud
            float : The cloud coverage in 8ths of the sky.

        Parameters
        ----------
        cloud_db : str, opt
            The full path name for the cloud database. Default None,
            which will use the database stored in the module ($SIMS_CLOUDMODEL_DIR/data/cloud.db).
        """
        self.cloud_db = cloud_db
        if self.cloud_db is None:
            self.cloud_db = os.path.join(getPackageDir('sims_cloudModel'), 'data', 'cloud.db')
        with sqlite3.connect(self.cloud_db) as conn:
            cur = conn.cursor()
            query = "select c_date, cloud from Cloud order by c_date;"
            cur.execute(query)
            results = np.array(cur.fetchall())
            self.cloud_dates = np.hsplit(results, 2)[0].flatten()
            self.cloud_values = np.hsplit(results, 2)[1].flatten()
            cur.close()
        # Make sure seeing dates are ordered appropriately (monotonically increasing).
        ordidx = self.cloud_dates.argsort()
        self.cloud_dates = self.cloud_dates[ordidx]
        self.cloud_values = self.cloud_values[ordidx]
        # Record this information, in case the cloud database does not start at t=0.
        self.min_time = self.cloud_dates[0]
        self.max_time = self.cloud_dates[-1]
        self.time_range = self.max_time - self.min_time
