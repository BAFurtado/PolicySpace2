""" Introducing a Central Bank that sells titles and provide interest set by the Government
    Eventually, it will loan to other banks

    Banks will serve to offer real estate loans
    """
import datetime
from collections import defaultdict
from functools import partial
from numpy import fv

import conf


class Loan:
    def __init__(self, principal, interest_rate):
        self.principal = principal
        self.balance = principal * (1+interest_rate)

        self.delinquent = False
        self.annual_payment = self.balance/conf.PARAMS['LOAN_SCHEDULE']

    def pay(self, amount):
        self.balance -= amount
        if amount < self.annual_payment:
            self.delinquent = True
            # TODO, how to spread out missed payment?

        # Fully paid off
        return self.balance <= 0


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

        # Track remaining loan balances
        self.loans = defaultdict(list)

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
        # TODO is it ok if the bank's balance becomes negative?
        self.balance -= interest - tax
        return interest - tax

    def deposit(self, client, amount, data):
        """ Receives the money of the client
        """
        try:
            self.wallet[client] += amount, data
        except TypeError:
            self.wallet[client] = amount, data
        self.balance += amount

    def withdraw(self, client, y, m):
        """ Gives the money back to the client
        """
        interest = self.pay_interest(client, y, m)
        amount = self.sum_deposits(client)
        del self.wallet[client]
        self.balance -= amount
        return amount + interest

    def sum_deposits(self, client):
        return sum([self.wallet[client][i]
                   for i in range(len(self.wallet[client]))
                   if i % 2 == 0])

    def total_deposits(self):
        return sum(v[0] for v in self.wallet.values())

    def request_loan(self, family, amount):
        # Can't loan more than on hand
        if amount < self.balance:
            return False

        # Add loan balance
        self.loans[family.id].append(Loan(amount, self.interest))
        self.balance -= amount
        return True

    def collect_loan_payments(self, families):
        for family_id, loans in self.loans.items():
            # TODO what if a family dies or splits etc
            family = families[family_id]
            remaining_loans = []
            for loan in loans:
                # TODO where does the family money come from?
                # TODO need to subtract from family money
                # What happens if family can't pay? shortfall distributed across subsequent payments?
                money = family.get_total_balance()
                payment = min(money, loan.annual_payment)
                done = loan.pay(payment)

                # Add to bank balance
                self.balance += payment

                # Remove loans that are paid off
                if not done:
                    remaining_loans.append(loan)
            self.loans[family_id] = remaining_loans


class Bank(Central):
    """ Market banks
        Yet to be designed

        May benefit from methods available at the Central Bank
        """
    pass


if __name__ == '__main__':
    BC = Central(0)
    b1 = Bank(0)
