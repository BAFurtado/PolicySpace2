from .product import Product


class Firm:
    """
    Firms contain all elements connected with firms, their methods to handle production, adding, paying
    and firing employees, maintaining information about their current staff, and available products, as
    well as cash flow. Decisions are based on endogenous variables and products are available when
    searched for by consumers.
    """

    def __init__(self, id,
                 address,
                 total_balance,
                 region_id,
                 profit=1,
                 amount_sold=0,
                 product_index=0,
                 amount_produced=0,
                 wages_paid=0,
                 actual_month=0,
                 revenue=0,
                 taxes_paid=0):

        self.id = id
        self.address = address
        self.total_balance = total_balance
        self.region_id = region_id
        self.profit = profit
        # Pool of workers in a given firm
        self.employees = {}
        # Firms makes existing products from class Products.
        # Products produced are stored by product_id in the inventory
        self.inventory = {}
        self.amount_sold = amount_sold
        self.product_index = product_index
        self.amount_produced = amount_produced
        self.wages_paid = wages_paid
        self.actual_month = actual_month
        self.revenue = revenue
        self.taxes_paid = taxes_paid

    # Product procedures ##############################################################################################
    def create_product(self):
        """Check for and create new products.
        Products are only created if the firms' balance is positive."""
        if self.profit > 0:
            dummy_quantity = 0
            dummy_price = 1
            if self.product_index not in self.inventory:
                self.inventory[self.product_index] = Product(self.product_index, dummy_quantity, dummy_price)
                self.product_index += 1
            self.prices = sum(p.price for p in self.inventory.values()) / len(self.inventory)

    def update_product_quantity(self, alpha, production_magnitude):
        """Production equation = Labour * qualification ** alpha"""
        if self.employees and self.inventory:
            # Call get_sum_qualification below: sum([employee.qualification ** parameters.ALPHA
            #                                   for employee in self.employees.values()])

            # Divide production by an order of magnitude adjustment parameter
            quantity = self.total_qualification(alpha) / production_magnitude
            for p in self.inventory.values():
                p.quantity += quantity
                self.amount_produced += quantity

    @property
    def total_quantity(self):
        return sum(p.quantity for p in self.inventory.values())

    def update_prices(self, sticky_prices, markup, seed):
        """Update prices based on sales"""
        # Sticky prices (KLENOW, MALIN, 2010)
        if seed.random() > sticky_prices:
            for p in self.inventory.values():
                # if firm has sold more than produced, prices rise
                if self.amount_sold > self.total_quantity:
                    p.price *= (1 + markup)
            # Easy to implement large discounts (that have to be permanent though)
        self.prices = sum(p.price for p in self.inventory.values()) / len(self.inventory)

    def sale(self, amount, regions, tax_consumption):
        """Sell max amount of products for a given amount of money"""
        if amount > 0:
            # For each product in this firms' inventory, spend amount proportionally
            dummy_bought_quantity = 0
            amount_per_product = amount / len(self.inventory)

            # Add price of the unit, deduce it from consumers' amount
            for key in list(self.inventory.keys()):
                if self.inventory[key].quantity > 0:
                    bought_quantity = amount_per_product / self.inventory[key].price

                    # Verifying if demand is within firms' available inventory
                    if bought_quantity > self.inventory[key].quantity:
                        bought_quantity = self.inventory[key].quantity
                        amount_per_product = bought_quantity * self.inventory[key].price

                    # Deducing from stock
                    self.inventory[key].quantity -= bought_quantity

                    # Tax deducted from firms' balance and value of sale added to the firm
                    self.total_balance += (amount_per_product - (amount_per_product * tax_consumption))

                    # Tax added to region-specific government
                    regions[self.region_id].collect_taxes(amount_per_product * tax_consumption,
                                                          'consumption')

                    # Quantifying quantity sold
                    dummy_bought_quantity += bought_quantity

                    # Deducing money from clients upfront
                    amount -= amount_per_product
            self.amount_sold += dummy_bought_quantity
        # Return any change
        return amount

    @property
    def num_products(self):
        return len(self.inventory)

    # Employees' procedures ##########################################################################################
    def add_employee(self, employee):
        # Adds a new employee to firms' set
        # Employees are instances of Agents
        self.employees[employee.id] = employee
        employee.firm_id = self.id

    def obit(self, employee):
        del self.employees[employee.id]

    def fire(self, seed):
        if self.employees:
            id = seed.choice(list(self.employees.keys()))
            self.employees[id].firm_id = None
            self.employees[id].commute = None
            del self.employees[id]

    def is_worker(self, id):
        # Returns true if agent is a member of this firm
        return id in self.employees

    @property
    def num_employees(self):
        return len(self.employees)

    def total_qualification(self, alpha):
        return sum([employee.qualification ** alpha for employee in self.employees.values()])

    def wage_base(self, unemployment, tax_consumption, ignore_unemployment):
        base = self.revenue * (1 - tax_consumption)
        if not ignore_unemployment:
            base *= (1 - unemployment)
        return base

    def make_payment(self, regions, unemployment, alpha, tax_labor, tax_consumption, ignore_unemployment):
        """Pay employees based on a base wage, relative employee qualification,
        consumption & labor taxes, and alpha param"""
        if self.employees:
            total_salary_paid = self.wage_base(unemployment, tax_consumption, ignore_unemployment=ignore_unemployment)
            if total_salary_paid > 0:
                total_qualification = self.total_qualification(alpha)
                for employee in self.employees.values():
                    # Making payment according to employees' qualification.
                    # Deducing it from firms' balance
                    # Deduce LABOR TAXES
                    wage = (total_salary_paid * (employee.qualification ** alpha)
                            / total_qualification) * (1 - tax_labor)
                    employee.money += wage
                    employee.last_wage = wage

                # Transfer collected LABOR TAXES to region
                regions[self.region_id].collect_taxes(total_salary_paid * tax_labor, 'labor')
                self.total_balance -= total_salary_paid
                self.wages_paid = total_salary_paid

    # Profits  #######################################################################################################
    # Save values in time, every quarter
    def calculate_profit(self):
        # Calculate profits considering last month wages paid,
        self.profit = self.revenue - self.wages_paid - self.taxes_paid

    def calculate_revenue(self):
        # Calculate revenue using monthly amount sold times prices applied in that month
        self.revenue = self.amount_sold * self.prices

    def pay_taxes(self, regions, unemployment, tax_consumption, tax_firm):
        taxes = (self.revenue - self.wages_paid) * tax_firm
        if taxes >= 0:
            # Revenue minus salaries paid in previous month may be negative.
            # In this case, no taxes are paid
            self.taxes_paid = taxes
            regions[self.region_id].collect_taxes(self.taxes_paid, 'firm')

    def __repr__(self):
        return 'FirmID: %s, $ %d, Emp. %d, Quant. %d, Address: %s at %s' % (self.id,
                                                                            self.total_balance,
                                                                            self.num_employees,
                                                                            self.total_quantity,
                                                                            self.address,
                                                                            self.region_id)
