import lsst.pex.config as pexConfig


__all__ = ['CloudModelConfig']


class CloudModelConfig(pexConfig.Config):
    """A pex_config configuration class for default seeing model parameters.
    """
    efd_columns = pexConfig.ListField(doc="List of data required from EFD",
                                      dtype=str,
                                      default=['cloud'])
    efd_delta_time = pexConfig.Field(doc="Length (delta time) of history to request from the EFD (seconds)",
                                     dtype=float,
                                     default=0)
    target_columns = pexConfig.ListField(doc="List of columns required from Scheduler target maps",
                                         dtype=str,
                                         default=['altitude', 'azimuth'])
    model_keys = pexConfig.ListField(doc="List of keys referring to the data returned from the model",
                                     dtype=str,
                                     default=['cloud'])
