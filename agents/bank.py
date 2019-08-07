""" Introducing a Central Bank that sells titles and provide interest set by the Government
    Eventually, it will loan to other banks

    Banks will serve to offer real estate loans
    """
import datetime
from collections import defaultdict
from functools import partial

import conf


class Central:
    """ The Central Bank
        Given a set rate of real interest rates, it provides capital remuneration
        (internationally, exogenously provided for the moment)
        """
    def __init__(self, id_):
        self.id = id_
        self.balance = 0
        self.interest = conf.PARAMS['INTEREST_RATE']
        self.wallet = d = defaultdict(partial(defaultdict, int, datetime))

    def pay_interest(self, client):
        """ Gives back only the interest to the client
        """
        pass

    def deposit(self, client):
        """ Receives the money of the client
        """
        pass

    def withdraw(self, client):
        """ Gives the money back to the client
        """
        pass


class Bank(Central):
    """ Market banks
        Yet to be designed

        May benefit from methods available at the Central Bank
        """
    pass


if __name__ == '__main__':
    BC = Central(0)
    b1 = Bank(0)
