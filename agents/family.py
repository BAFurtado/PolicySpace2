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
    def sum_balance(self):
        """Calculates the total available balance of the family"""
        self.balance = sum(m.money for m in self.members.values())
        return self.balance

    def update_balance(self, amount):
        """Evenly distribute money to each member"""
        if self.members:
            per_member = amount / float(self.num_members)
            for member in self.members.values():
                member.money += per_member

    def grab_savings(self):
        """Withdraws total available balance of the family"""
        s = self.savings
        self.savings = 0
        return s

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
    def to_consume(self):
        """Grabs all money from all members"""
        return sum(m.grab_money() for m in self.members.values())

    def consume(self, firms, regions, params, seed):
        """Family spends a random amount of money, based on the BETA parameter,
        on a single firm's goods, chosen either by (closest) distance or (cheapest) price.
        Amount bought is maximum allowable amount (given firm inventory and spendable money)"""
        money = self.to_consume()
        # Decision on how much money to spend
        # Deduced by parameter Beta
        if money > 0:
            if money < 1:
                # As beta is an exponential, when money is below 1, choose a value between 0 and 1
                money_to_spend = seed.uniform(0, money)
            else:
                # When money is 1 or above, choose a value to spend between 0 and total discounted by beta
                money_to_spend = money * seed.betavariate(1, (1 - params['BETA'])/params['BETA'])

            # Picks SIZE_MARKET number of firms at seed and choose the closest or the cheapest
            # Consumes from each product the chosen firm offers
            market = seed.sample(firms, min(len(firms), int(params['SIZE_MARKET'])))
            # Choose between cheapest or closest
            firm_strategy = seed.random()
            self.firm_strategy = 'Price' if firm_strategy < 0.5 else 'Distance'

            if firm_strategy < 0.5:
                # Choose firm with cheapest average prices
                chosen_firm = min(market, key=lambda firm: firm.prices)
            else:
                # Choose closest firm
                chosen_firm = min(market, key=lambda firm: self.house.distance_to_firm(firm))

            # Buy from chosen company
            change = chosen_firm.sale(money_to_spend, regions, params['TAX_CONSUMPTION'])
            money -= (money_to_spend - change)
            # Rounding values

            self.savings += money

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
               (self.id, self.house.id if self.house else None, self.savings, self.sum_balance())
