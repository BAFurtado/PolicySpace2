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
        self.owned_houses = list()
        self.members = {}
        self.relatives = set()
        # Refers to the house the family is living on currently
        self.house = house
        self.rent_default = 0
        self.rent_voucher = 0
        self.average_utility = 0
        self.last_permanent_income = list()

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
        if house.family_id is None:
            self.house = house
            house.family_id = self.id
            self.region_id = house.region_id
        else:
            raise Exception

    def move_out(self, funds):
        # If family still has policy money for rent payment and is moving out, give back the money to municipality
        if self.house.rent_data:
            if self.rent_voucher:
                funds.policy_money[self.region_id[:7]] += self.rent_voucher * self.house.rent_data[0]
                self.rent_voucher = 0
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
            per_member = amount / self.num_members
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
        return self.savings + estate_value + bank.sum_deposits(self) - bank.loan_balance(self.id)

    def invest(self, r, bank, y, m):
        # Savings is updated during consumption as the fraction of above permanent income that is not consumed
        # If savings is above a six-month period reserve money, the surplus is invested in the bank.
        reserve_money = self.get_permanent_income() * 6
        if self.savings > reserve_money > 0:
            bank.deposit(self, self.savings - reserve_money, datetime.date(y, m, 1))
            self.savings = reserve_money

    def total_wage(self):
        return sum(member.last_wage for member in self.members.values() if member.last_wage is not None)

    def get_permanent_income(self):
        return sum(self.last_permanent_income) / len(self.last_permanent_income) if self.last_permanent_income else 0

    def permanent_income(self, bank, r):
        # Equals Consumption (Bielefeld, 2018, pp.13-14)
        # Using last wage available as base for permanent income calculus: total_wage = Human Capital
        t0 = self.total_wage()
        r_1_r = r/(1 + r)
        # Calculated as "discounted sum of current income and expected future income" plus "financial wealth"
        # Perpetuity of income is a fraction (r_1_r) of income t0 divided by interest r
        self.last_permanent_income.append(r_1_r * t0 + r_1_r * (t0 / r) + self.get_wealth(bank) * r)
        return self.get_permanent_income()

    def prop_employed(self):
        """Proportion of members that are employed"""
        employable = [m for m in self.members.values() if 16 < m.age < 70]
        return len([m for m in employable if m.firm_id is None])/len(employable) if employable else 0

    # Consumption ####################################################################################################
    def to_consume(self, central, r, year, month):
        """Grabs all money from all members"""
        money = sum(m.grab_money() for m in self.members.values())
        permanent_income = self.permanent_income(central, r)
        # Having loans will impact on a lower long-run permanent income consumption and on a monthly strongly
        # reduction of consumption. However, the price of the house may be appreciating in the market.
        # If cash at hand is positive consume it capped to permanent income
        money_to_spend = None
        if money > 0:
            if money > permanent_income > 0:
                money_to_spend = permanent_income
                # Deposit family money above that of permanent income
                self.savings += money - permanent_income
            else:
                money_to_spend = money
        # If there is no cash available, withdraw at most permanent income from savings
        elif self.savings > permanent_income > 0:
            self.savings -= permanent_income
            money_to_spend = permanent_income
        elif self.savings > 0:
            money_to_spend = self.savings
            self.savings = 0
        else:
            # If there is no cash and no savings withdraw from any long-term deposits if any
            if central.wallet[self]:
                cash = self.grab_savings(central, year, month)
                if cash > permanent_income:
                    cash -= permanent_income
                    money_to_spend = permanent_income
                else:
                    money_to_spend = cash
        return money_to_spend

    def consume(self, firms, central, regions, params, seed, year, month):
        """Family consumes its permanent income, based on members wages, working life expectancy
        and real estate and savings real interest
        """
        money_to_spend = self.to_consume(central, central.interest, year, month)
        # Decision on how much money to consume or save

        if money_to_spend is not None:
            # Picks SIZE_MARKET number of firms at seed and choose the closest or the cheapest
            # Consumes from each product the chosen firm offers
            market = seed.sample(firms, min(len(firms), int(params['SIZE_MARKET'])))
            market = [firm for firm in market if firm.total_quantity > 0]
            if market:
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
                self.average_utility = money_to_spend - change

    @property
    def agents(self):
        return list(self.members.values())

    def is_member(self, _id):
        return _id in self.members

    @property
    def num_members(self):
        return len(self.members)

    def __repr__(self):
        return 'Family ID %s, House ID %s, Savings $ %.2f, Balance $ %.2f' % \
               (self.id, self.house.id if self.house else None, self.savings, self.get_total_balance())

    @property
    def is_renting(self):
        return self.house.rent_data is not None
