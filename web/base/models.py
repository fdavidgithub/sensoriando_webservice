from .legacy import *

class eThings(Things):
    def __str__(self):
        return self.name

class eSensors(Sensors):
    def __str__(self):
        return self.name

class eAccounts(Accounts):
    def __str__(self):
        return "%s %s" % (self.city, self.ispublic)


