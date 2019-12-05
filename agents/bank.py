""" Introducing a Central Bank that sells titles and provide interest set by the Government
    Eventually, it will loan to other banks

    Banks will serve to offer real estate loans
    """
import datetime
from collections import defaultdict
from functools import partial
from numpy import fv

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
        self.wallet = defaultdict(partial(defaultdict, float, datetime))
        self.taxes = 0

    def pay_interest(self, client, y, m):
        """ Updates interest to the client
        """
        # Compute future values
        interest = 0
        for i in range(len(self.wallet[client])):
            if i % 2 == 0:
                interest += fv(self.interest/12,
                               (datetime.date(y, m, 1) - self.wallet[client][i + 1]).days // 30,
                               0,
                               self.wallet[client][i] * -1)
                interest -= self.wallet[client][i]

        # Compute taxes
        tax = interest * .15
        self.taxes += tax
        self.balance -= interest - tax
        return interest - tax

    def deposit(self, client, amount, data):
        """ Receives the money of the client
        """
        try:
            self.wallet[client] += amount, data
        except TypeError:
            self.wallet[client] = amount, data

    def withdraw(self, client, y, m):
        """ Gives the money back to the client
        """
        interest = self.pay_interest(client, y, m)
        amount = self.sum_deposits(client)
        del self.wallet[client]
        return amount + interest

    def sum_deposits(self, client):
        return sum([self.wallet[client][i]
                   for i in range(len(self.wallet[client]))
                   if i % 2 == 0])

    def total_deposits(self):
        return sum(v[0] for v in self.wallet.values())


class Bank(Central):
    """ Market banks
        Yet to be designed

        May benefit from methods available at the Central Bank
        """
    pass


if __name__ == '__main__':
    BC = Central(0)
    b1 = Bank(0)
