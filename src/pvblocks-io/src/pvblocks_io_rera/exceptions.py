class NoResponseException(Exception):
    '''No response from system.'''
    def __str__(self):
        return self.__doc__

class UnexpectedResponseException(Exception):
    '''Unexpected response from system.'''
    def __str__(self):
        return self.__doc__