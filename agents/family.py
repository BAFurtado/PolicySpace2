import datetime


class Family:
    """
    Family class. Nothing but a bundle of Agents together.
    Generated once and fixed.
    Families share resources equally and move together from household to household.
    Children, when born, remain inside the same family.

    - Setup family class
    - Relevant to distribute income among family members
    - Mobile, as it changes houses when in the housing market
    """

    def __init__(self, _id,
                 balance=0,
                 savings=0,
                 house=None):
        self.id = _id
        self.balance = balance
        self.savings = savings
        self.wealth = None
        self.owned_houses = list()
        self.members = {}
        self.relatives = set()
        # Refers to the house the family is living on currently
        self.house = house
        self.average_utility = 0
        self.monthly_loan_payments = 0
        self.last_permanent_income = 0

        # Previous region id
        if house is not None:
            self.region_id = house.region_id
        else:
            self.region_id = None

    def add_agent(self, agent):
        """Adds a new agent to the set"""
        self.members[agent.id] = agent
        agent.family = self

    def remove_agent(self, agent):
        agent.family = None
        del self.members[agent.id]

    def move_in(self, house):
        self.house = house
        house.family_id = self.id
        self.region_id = house.region_id

    def move_out(self):
        self.house.empty()
        self.house = None

    @property
    def address(self):
        if self.house is not None:
            return self.house.address

    # Budget operations ##############################################################################################
    def get_total_balance(self):
        """Calculates the total available balance of the family"""
        self.balance = sum(m.money for m in self.members.values())
        return self.balance

    def update_balance(self, amount):
        """Evenly distribute money to each member"""
        if self.members:
            per_member = amount / float(self.num_members)
            for member in self.members.values():
                member.money += per_member

    def grab_savings(self, bank, y, m):
        """Withdraws total available balance of the family"""
        s = self.savings
        self.savings = 0
        s += bank.withdraw(self, y, m)
        return s

    def get_wealth(self, bank):
        """ Calculate current wealth, including real estate. """
        estate_value = sum(h.price for h in self.owned_houses)
        return self.savings + estate_value - bank.loan_balance(self.id)

    def invest(self, r, bank, y, m):
        # Savings is updated during consumption as the fraction of above permanent income that is not consumed
        # If savings is above a six-month period reserve money, the surplus is invested in the bank.
        reserve_money = self.permanent_income(bank, r) * 6
        if self.savings > reserve_money:
            bank.deposit(self, self.savings - reserve_money, datetime.date(y, m, 1))

    def total_wage(self):
        return sum(member.last_wage for member in self.members.values() if member.last_wage is not None)

    def permanent_income(self, bank, r):
        # Equals Consumption (Bielefeld, 2018, pp.13-14)
        # Using last wage available as base for permanent income calculus: total_wage = Human Capital
        t0 = self.total_wage()
        r_1_r = r/(1 + r)
        # Calculated as "discounted some of current income and expected future income" plus "financial wealth"
        # Perpetuity of income is a fraction (r_1_r) of income t0 divided by interest r
        self.last_permanent_income = r_1_r * t0 + r_1_r * (t0 / r) + self.get_wealth(bank) * r
        return self.last_permanent_income

    def prop_employed(self):
        """Proportion of members that are employed"""
        unemployed, employed = 0, 0
        for member in self.members.values():
            if member.is_employable:
                unemployed += 1
            elif member.is_employed:
                employed += 1
        if employed + unemployed == 0:
            return 0
        else:
            return employed / (employed + unemployed)

    # Consumption ####################################################################################################
    def to_consume(self, central, r):
        """Grabs all money from all members"""
        money = sum(m.grab_money() for m in self.members.values())
        permanent_income = self.permanent_income(central, r)
        permanent_income -= self.monthly_loan_payments
        # Having loans will impact on a lower long-run permanent income consumption and on a monthly strongly
        # reduction of consumption. However, the price of the house may be appreciating in the market.
        # If cash at hand is positive consume it capped to permanent income
        if money > 0:
            if money > permanent_income:
                money_to_spend = permanent_income
                # Deposit family money above that of permanent income
                self.savings += money - permanent_income
            else:
                money_to_spend = money
            return money_to_spend
        # If there is no cash available, withdraw at most permanent income from savings
        elif self.savings > permanent_income:
            self.savings -= permanent_income
            return permanent_income
        elif self.savings > 0:
            money_to_spend = self.savings
            self.savings = 0
            return money_to_spend
        else:
            # If there is no cash and no savings, pass
            # TODO: should keep tabs on how many families go hungry
            return None

    def consume(self, firms, central, regions, params, seed):
        """Family consumes its permanent income, based on members wages, working life expectancy
        and real estate and savings real interest
        """
        money_to_spend = self.to_consume(central, params['INTEREST_RATE'])
        # Decision on how much money to consume or save

        if money_to_spend is not None:
            # Picks SIZE_MARKET number of firms at seed and choose the closest or the cheapest
            # Consumes from each product the chosen firm offers
            market = seed.sample(firms, min(len(firms), int(params['SIZE_MARKET'])))
            # Choose between cheapest or closest
            firm_strategy = seed.choice(['Price', 'Distance'])

            if firm_strategy == 'Price':
                # Choose firm with cheapest average prices
                chosen_firm = min(market, key=lambda firm: firm.prices)
            else:
                # Choose closest firm
                chosen_firm = min(market, key=lambda firm: self.house.distance_to_firm(firm))

            # Buy from chosen company
            change = chosen_firm.sale(money_to_spend, regions, params['TAX_CONSUMPTION'])
            self.savings += change

            # Update family utility
            utility = money_to_spend - change
            self.distribute_utility(utility)

    def distribute_utility(self, utility):
        """Evenly distribute utility to each member"""
        if self.members:
            utilities = []
            amount = utility / float(self.num_members)
            for member in self.members.values():
                member.utility += amount
                utilities.append(member.utility)
            self.average_utility = sum(utilities) / float(self.num_members)
        else:
            self.average_utility = 0

    @property
    def agents(self):
        return list(self.members.values())

    def is_member(self, id):
        return id in self.members

    @property
    def num_members(self):
        return len(self.members)

    def __repr__(self):
        return 'Family ID %s, House ID %s, Savings $ %.2f, Balance $ %.2f' % \
               (self.id, self.house.id if self.house else None, self.savings, self.get_total_balance())

    @property
    def is_renting(self):
        return self.house.rent_data is not None
