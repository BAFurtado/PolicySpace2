from .house import House
from .product import Product
from collections import defaultdict


class Firm:
    """
    Firms contain all elements connected with firms, their methods to handle production, adding, paying
    and firing employees, maintaining information about their current staff, and available products, as
    well as cash flow. Decisions are based on endogenous variables and products are available when
    searched for by consumers.
    """
    type = 'CONSUMER'

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
                 taxes_paid=0,
                 prices=None):

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
        self.prices = prices

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

    # Production department
    def update_product_quantity(self, alpha, production_magnitude):
        """Production equation = Labor * qualification ** alpha"""
        if self.employees and self.inventory:
            # Call get_sum_qualification below: sum([employee.qualification ** parameters.ALPHA
            #                                   for employee in self.employees.values()])

            # Divide production by an order of magnitude adjustment parameter
            quantity = self.total_qualification(alpha) / production_magnitude
            # Currently, each firm has only a single product. If more products should be introduced, allocation of
            # quantity per product should be adjusted accordingly
            # Currently, the index for the single product is 0
            self.inventory[0].quantity += quantity
            self.amount_produced += quantity

    @property
    def total_quantity(self):
        return sum(p.quantity for p in self.inventory.values())

    # Commercial department
    def update_prices(self, sticky_prices, markup, seed):
        """Update prices based on sales"""
        # Sticky prices (KLENOW, MALIN, 2010)
        if seed.random() > sticky_prices:
            for p in self.inventory.values():
                # if the firm has sold more than available in stocks, prices rise
                if self.amount_sold > self.total_quantity:
                    p.price *= (1 + markup)
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
                    revenue = (amount_per_product - (amount_per_product * tax_consumption))
                    self.total_balance += revenue
                    self.revenue += revenue

                    # Tax added to region-specific government
                    regions[self.region_id].collect_taxes(amount_per_product * tax_consumption, 'consumption')

                    # Quantifying quantity sold
                    dummy_bought_quantity += bought_quantity

                    # Deducing money from clients upfront
                    amount -= amount_per_product
            self.amount_sold += dummy_bought_quantity
        # Return change to consumer, if any
        return amount

    @property
    def num_products(self):
        return len(self.inventory)

    # Accountancy department ########################################################################################
    # Save values in time
    def calculate_profit(self):
        # Calculate profits considering last month wages paid and taxes on firm
        # (labor and consumption taxes are already deducted)
        self.profit = self.revenue - self.wages_paid - self.taxes_paid

    def pay_taxes(self, regions, tax_firm):
        taxes = (self.revenue - self.wages_paid) * tax_firm
        if taxes >= 0:
            # Revenue minus salaries paid in previous month may be negative.
            # In this case, no taxes are paid
            self.taxes_paid = taxes
            self.total_balance -= taxes
            regions[self.region_id].collect_taxes(self.taxes_paid, 'firm')

    # Employees' procedures #########
    def total_qualification(self, alpha):
        return sum([employee.qualification ** alpha for employee in self.employees.values()])

    def wage_base(self, unemployment, ignore_unemployment):
        if not ignore_unemployment:
            # Observing global economic performance has the added advantage of not spending all revenue on salaries
            return self.revenue * (1 - unemployment)
        else:
            return self.revenue

    def make_payment(self, regions, unemployment, alpha, tax_labor, ignore_unemployment):
        """Pay employees based on revenue, relative employee qualification, labor taxes, and alpha param"""
        if self.employees:
            # Total salary, including labor taxes
            total_salary_paid = self.wage_base(unemployment, ignore_unemployment=ignore_unemployment)
            if total_salary_paid > 0:
                total_qualification = self.total_qualification(alpha)
                for employee in self.employees.values():
                    # Making payment according to employees' qualification.
                    # Deducing it from firms' balance
                    # Deduce LABOR TAXES from employees' salaries as a percentual of each salary
                    wage = (total_salary_paid * (employee.qualification ** alpha)
                            / total_qualification) * (1 - tax_labor)
                    employee.money += wage
                    employee.last_wage = wage

                # Transfer collected LABOR TAXES to region
                labor_tax = total_salary_paid * tax_labor
                regions[self.region_id].collect_taxes(labor_tax, 'labor')
                self.total_balance -= total_salary_paid
                self.wages_paid = total_salary_paid

    # Human resources department #################
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

    def get_total_balance(self):
        return self.total_balance

    def __repr__(self):
        return 'FirmID: %s, $ %d, Emp. %d, Quant. %d, Address: %s at %s' % (self.id,
                                                                            self.total_balance,
                                                                            self.num_employees,
                                                                            self.total_quantity,
                                                                            self.address,
                                                                            self.region_id)


class ConstructionFirm(Firm):
    type = 'CONSTRUCTION'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.houses = []
        self.houses_inventory = []
        self.building = False
        self.building_region = None
        self.building_size = None
        self.building_cost = None
        self.building_quality = None
        self.cash_flow = defaultdict(float)

    def plan_house(self, regions, houses, lot_price, markup, seed):
        """Decide where to build"""
        if self.building:
            return

        # Candidate regions for licenses and check of funds to buy license
        regions = [r for r in regions if r.licenses > 0 and self.total_balance > r.license_price]
        if not regions:
            return

        # Targets
        building_size = seed.randrange(20, 120)
        building_quality = seed.choice([1, 2, 3, 4])

        # Get information about region house prices
        region_ids = [r.id for r in regions]
        region_prices = defaultdict(list)
        for h in houses:
            # In correct region,
            # within 10 size units,
            # within 1 quality
            if h.region_id in region_ids\
                    and abs(h.size - building_size) <= 10\
                    and abs(h.quality - building_quality) <= 1:
                region_prices[h.region_id].append(h.price)
                # Only take a sample
                if len(region_prices[h.region_id]) > 100:
                    region_ids.remove(h.region_id)
                    if not region_ids:
                        break

        # Number of product quantities needed for the house
        gross_cost = building_size * building_quality
        # Productivity of the company may vary double than exogenous set markup.
        # Productivity reduces the cost of construction and sets the size of profiting when selling
        productivity = seed.randint(100 - int(2 * markup * 100), 100) / 100
        building_cost = gross_cost * productivity

        # Choose region where construction is most profitable
        # There might not be samples for all regions, so fallback to price of 0
        region_mean_prices = {r_id: sum(vs)/len(vs) for r_id, vs in region_prices.items()}
        region_profitability = [region_mean_prices.get(r.id, 0) - (r.license_price * building_cost * (1 + lot_price))
                                for r in regions]
        regions = [(r, p) for r, p in zip(regions, region_profitability) if p > 0]

        # No profitable regions
        if not regions:
            return

        # Choose region with highest profitability
        region = max(regions, key=lambda rp: rp[1])[0]
        self.building_region = region.id
        self.building_size = building_size
        self.building_quality = building_quality
        #
        # Product.quantity increases as construction moves forward and is deducted at once
        self.building_cost = building_cost * region.license_price
        self.building = True

        # Buy license
        region.licenses -= 1
        # Region license price is current QLI. Lot price is the model parameter
        cost_of_land = region.license_price * building_cost * lot_price
        self.total_balance -= cost_of_land
        region.collect_taxes(cost_of_land, 'transaction')

    def build_house(self, regions, generator):
        """Firm decides if house is finished"""
        if not self.building:
            return

        # Not finished
        if self.total_quantity < self.building_cost:
            return

        # Finished, expend inputs
        for k, product in self.inventory.items():
            paid = min(self.building_cost, product.quantity)
            product.quantity -= paid
            self.building_cost -= paid

        # Choose random place in region
        region = regions[self.building_region]
        probability_urban = generator.prob_urban(region)
        address = generator.random_address(region, probability_urban)

        # Create the house
        house_id = generator.gen_id()
        size = self.building_size
        quality = self.building_quality
        price = (size * quality) * region.index
        h = House(house_id, address, size, price, region.id, quality, owner_id=self.id, owner_type=House.Owner.FIRM)
        self.houses.append(h)
        self.houses_inventory.append(h)

        self.building = False
        return h

    # Selling house
    def update_balance(self, amount, acc_months=None):
        self.total_balance += amount
        if acc_months is not None:
            self.update_cash_flow(amount, acc_months)

    def update_cash_flow(self, amount, acc_months):
        for i in range(acc_months):
            self.cash_flow[i] += amount/acc_months

    def wage_base(self, unemployment, ignore_unemployment):
        self.revenue = self.cash_flow[self.actual_month]
        self.cash_flow[self.actual_month] = 0
        if not ignore_unemployment:
            # Observing global economic performance has the added advantage of not spending all revenue on salaries
            return self.revenue * (1 - unemployment)
        else:
            return self.revenue

    @property
    def n_houses_sold(self):
        return len(self.houses) - len(self.houses_inventory)

    def mean_house_price(self):
        if not self.houses:
            return 0
        t = sum(h.price for h in self.houses)
        return t/len(self.houses)
