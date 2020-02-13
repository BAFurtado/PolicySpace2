""" Introducing a Central Bank that sells titles and provide interest set by the Government
    Eventually, it will loan to other banks

    Banks will serve to offer real estate loans
    """
import datetime
from collections import defaultdict
from numpy import fv

import conf


class Loan:
    def __init__(self, principal, interest_rate, payment):
        self.age = 0
        self.principal = principal
        self.balance = principal * (1+interest_rate)
        self.payment = payment

        self.paid_off = False
        self.delinquent = False

    def pay(self, amount):
        self.balance -= amount
        if amount < self.payment:
            self.delinquent = True

        # Fully paid off
        self.paid_off = self.balance <= 0
        return self.paid_off


class Central:
    """ The Central Bank
        Given a set rate of real interest rates, it provides capital remuneration
        (internationally, exogenously provided for the moment)
        """
    def __init__(self, id_):
        self.id = id_
        self.balance = 0
        self.interest = conf.PARAMS['INTEREST_RATE']
        self.wallet = defaultdict(list)
        self.taxes = 0

        # Track remaining loan balances
        self.loans = defaultdict(list)

    def pay_interest(self, client, y, m):
        """ Updates interest to the client
        """
        # Compute future values
        interest = 0
        for amount, date in self.wallet[client]:
            interest += fv(self.interest,
                            (datetime.date(y, m, 1) - date).days // 30,
                            0,
                            amount * -1)
            interest -= amount

        # Compute taxes
        tax = interest * .15
        self.taxes += tax
        self.balance -= interest - tax
        return interest - tax

    def deposit(self, client, amount, date):
        """ Receives the money of the client
        """
        self.wallet[client].append((amount, date))
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
        return sum(amount for amount, _ in self.wallet[client])

    def total_deposits(self):
        return sum(sum(amount for amount, _ in deposits) for deposits in self.wallet.values())

    def n_loans(self):
        return sum(len(ls) for ls in self.loans.values())

    def all_loans(self):
        for ls in self.loans.values():
            yield from ls

    def active_loans(self):
        return [l for l in self.all_loans() if not l.paid_off]

    def delinquent_loans(self):
        return [l for l in self.active_loans() if l.delinquent]

    def loan_stats(self):
        loans = self.active_loans()
        amounts = [l.principal for l in loans]
        if amounts:
            mean = sum(amounts)/len(amounts)
            return min(amounts), max(amounts), mean
        return 0, 0, 0

    def request_loan(self, family, amount):
        # Can't loan more than on hand
        if amount > self.balance:
            return False

        # If they have outstanding loans, don't lend
        if self.loans[family.id]:
            return False

        # Add loan balance
        monthly_payment = self._max_monthly_payment(family)
        self.loans[family.id].append(Loan(amount, self.interest, monthly_payment))
        self.balance -= amount
        return True

    def max_loan(self, family):
        """Estimate maximum loan for family"""
        income = self._max_monthly_payment(family)

        max_years = conf.PARAMS['MAX_LOAN_AGE'] - max([m.age for m in family.members.values()])
        max_months = max_years * 12
        max_total = income * max_months
        max_principal = max_total/(1+self.interest)
        return min(max_principal, self.balance)

    def _max_monthly_payment(self, family):
        # Max % of income on loan repayments
        income = family.permanent_income(self.interest) * conf.PARAMS['MAX_LOAN_REPAYMENT_PERCENT_INCOME']

        # Account for existing loans
        for l in self.loans[family.id]:
            income -= l.payment
        return income

    def collect_loan_payments(self, sim):
        for family_id, loans in self.loans.items():
            if not loans: continue
            family = sim.families[family_id]
            remaining_loans = []
            for loan in loans:
                if loan.paid_off: continue
                loan.age += 1

                money = family.savings
                if money < loan.payment:
                    money = family.grab_savings(self, sim.clock.year,(sim.clock.months % 12) + 1)
                    family.savings = money
                payment = min(money, loan.payment)
                done = loan.pay(payment)
                family.savings -= payment

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
