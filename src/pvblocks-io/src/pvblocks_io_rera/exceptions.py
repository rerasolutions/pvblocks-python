class NoDeviceException(Exception):
    '''Can not access to device.'''
    def __str__(self):
        return self.__doc__
