class NoResponseException(Exception):
    '''No response from system.'''
    def __str__(self):
        return self.__doc__

class UnexpectedResponseException(Exception):
    '''Unexpected response from system.'''
    def __str__(self):
        return self.__doc__

class NoReadDataImplementedException(Exception):
    '''No read_data implemented for this blocktype.'''

    def __str__(self):
        return self.__doc__


class CannotOpenBlockException(Exception):
    '''Cannot open PVBlock.'''

    def __str__(self):
        return self.__doc__


class MethodNotSupportedException(Exception):
    '''Method not supported for PVBlock.'''

    def __str__(self):
        return self.__doc__


class PvBlocksIsNoneException(Exception):
    '''PVBlock is None'''

    def __str__(self):
        return self.__doc__