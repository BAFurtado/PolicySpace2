""" Introducing a Central Bank that sells titles and provide interest set by the Government
    Eventually, it will loan to other banks

    Banks will serve to offer real estate loans
    """
import datetime
from collections import defaultdict
from numpy import fv

import conf


class Loan:
    def __init__(self, principal, interest_rate, payment, house_collateral):
        self.age = 0
        self.principal = principal
        self.balance = principal * (1 + interest_rate)
        self.payment = payment
        self.missed = 0
        self.collateral = house_collateral
        self.paid_off = False
        self.delinquent = False

    def pay(self, amount):
        self.balance -= amount
        if amount < self.payment + self.missed:
            self.delinquent = True
            self.missed = self.payment - amount
        else:
            self.delinquent = False
            self.missed = 0

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

        self._outstanding_loans = 0
        self._total_deposits = 0

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
        tax = interest * conf.PARAMS['TAX_FIRM']
        self.taxes += tax
        self.balance -= interest - tax
        return interest - tax

    def collect_taxes(self):
        """ This function withdraws monthly collected taxes from investments, at tax firm rates and
            resets the counter back to 0.
            """
        amount, self.taxes = self.taxes, 0
        return amount

    def deposit(self, client, amount, date):
        """ Receives the money of the client
        """
        self.wallet[client].append((amount, date))
        self.balance += amount
        self._total_deposits += amount

    def withdraw(self, client, y, m):
        """ Gives the money back to the client
        """
        interest = self.pay_interest(client, y, m)
        amount = self.sum_deposits(client)
        del self.wallet[client]
        self.balance -= amount
        self._total_deposits -= amount
        return amount + interest

    def sum_deposits(self, client):
        return sum(amount for amount, _ in self.wallet[client])

    def total_deposits(self):
        return sum(sum(amount for amount, _ in deposits) for deposits in self.wallet.values())

    def loan_balance(self, family_id):
        """Get total loan balance for a family"""
        return sum(l.balance for l in self.loans.get(family_id, []))

    def n_loans(self):
        return sum(len(ls) for ls in self.loans.values())

    def outstanding_loan_balance(self):
        return sum(l.balance for l in self.all_loans())

    def all_loans(self):
        for ls in self.loans.values():
            yield from ls

    def prob_default(self):
        # Sum of loans of clients who are currently missing any payment divided by total outstanding loans.
        return sum([l.balance for l in self.delinquent_loans()]) / sum([l.balance for l in self.active_loans()])

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

    def request_loan(self, family, house_collateral, amount, seed):
        # Can't loan more than on hand
        if amount > self.balance:
            return False

        # If they have outstanding loans, don't lend
        if self.loans[family.id]:
            return False

        # Can't loan more than x% of total deposits
        if self._outstanding_loans + amount > self._total_deposits * conf.PARAMS['MAX_LOAN_BANK_PERCENT']:
            return False

        # Probability of giving loan depends on amount compared to family wealth. Credit check
        p = 1 - (amount/family.get_wealth(self))
        if seed.random() > p:
            return

        # Add loan balance
        monthly_payment = self._max_monthly_payment(family)
        self.loans[family.id].append(Loan(amount, self.interest, monthly_payment, house_collateral))
        family.monthly_loan_payments = sum(l.payment for l in self.loans[family.id])
        self.balance -= amount
        self._outstanding_loans += amount
        return True

    def max_loan(self, family):
        """Estimate maximum loan for family"""
        income = self._max_monthly_payment(family)

        max_years = conf.PARAMS['MAX_LOAN_AGE'] - max([m.age for m in family.members.values()])
        max_months = max_years * 12
        max_total = income * max_months
        max_principal = max_total/(1 + self.interest)
        return min(max_principal, self.balance)

    def _max_monthly_payment(self, family):
        # Max % of income on loan repayments
        return family.permanent_income(self, self.interest) * conf.PARAMS['DEBT_TO_INCOME']

    def collect_loan_payments(self, sim):
        for family_id, loans in self.loans.items():
            if not loans:
                continue
            family = sim.families[family_id]
            remaining_loans = []
            for loan in loans:
                if loan.paid_off:
                    continue
                loan.age += 1
                if family.savings < loan.payment + loan.missed:
                    family.savings += family.grab_savings(self, sim.clock.year, sim.clock.months)
                payment = min(family.savings, loan.payment + loan.missed)
                done = loan.pay(payment)
                family.savings -= payment

                # Add to bank balance
                self.balance += payment
                self._outstanding_loans -= payment

                # Remove loans that are paid off
                if not done:
                    remaining_loans.append(loan)
            self.loans[family_id] = remaining_loans
            family.monthly_loan_payments = sum(l.payment for l in remaining_loans)


class Bank(Central):
    """ Market banks
        Yet to be designed

        May benefit from methods available at the Central Bank
        """
    pass
