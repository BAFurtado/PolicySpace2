import datetime

import numpy as np


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

    def __init__(self, id,
                 balance=0,
                 savings=0,
                 house=None,
                 firm_strategy=None):
        self.id = id
        self.balance = balance
        self.savings = savings
        self.wealth = None
        self.owned_houses = list()
        self.members = {}
        self.house = house
        self.firm_strategy = firm_strategy
        self.average_utility = 0

    def add_agent(self, agent):
        """Adds a new agent to the set"""
        self.members[agent.id] = agent
        agent.family = self

    def remove_agent(self, agent):
        del self.members[agent.id]

    def move_out(self):
        if self.house is not None:
            self.house.empty()
            self.house = None

    def move_in(self, house):
        self.house = house
        house.family_id = self.id

    @property
    def address(self):
        if self.house is not None:
            return self.house.address

    @property
    def region_id(self):
        if self.house is not None:
            return self.house.region_id

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

    def grab_savings(self, central, y, m):
        """Withdraws total available balance of the family"""
        s = self.savings
        self.savings = 0
        s += central.withdraw(self, y, m)
        return s

    def get_wealth(self):
        """ Calculate current wealth, including real estate. """
        estate_value = sum(h.price for h in self.owned_houses)
        return self.savings + estate_value

    def invest(self, r, bank, y, m):
        liquid_money = self.savings > self.permanent_income(r) * 6
        if self.savings > liquid_money:
            bank.deposit(self, self.savings - liquid_money, datetime.date(y, m, 1))

    def human_capital(self, r):
        # Using retiring age minus current age as exponent s
        # Using last wage available as base for permanent income calculus
        ts = sum([np.pv(r/12, (74 - member.age) * 12, -member.last_wage)
                  for member in self.members.values()
                  if member.last_wage is not None])
        t0 = sum(member.last_wage for member in self.members.values() if member.last_wage is not None)
        return t0, ts

    def permanent_income(self, r):
        # Equals Consumption (Bielefeld, 2018, pp.13-14)
        t0, ts = self.human_capital(r)
        r_1_r = r/(1 + r)
        return r_1_r * t0 + r_1_r * ts + self.get_wealth() * r

    def average_study(self):
        """Averages the years of study of the family"""
        self.study = sum(m.qualification for m in self.members.values())
        if self.members:
            self.study /= float(self.num_members)
        return self.study

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
    def to_consume(self, r):
        """Grabs all money from all members"""
        money = sum(m.grab_money() for m in self.members.values())
        permanent_income = self.permanent_income(r)
        # If cash at hand is positive consume it capped to permanent income
        if money > 0:
            if money > permanent_income:
                money_to_spend = permanent_income
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
            return None

    def consume(self, firms, regions, params, seed):
        """Family consumes its permanent income, based on members wages, working life expectancy
        and real estate and savings real interest
        """
        money_to_spend = self.to_consume(params['INTEREST_RATE'])
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
