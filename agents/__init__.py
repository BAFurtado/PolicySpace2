from world.population import marriage_data
from .bank import Central
from .family import Family
from .firm import Firm, ConstructionFirm
from .house import House
from .region import Region


class Agent:
    """
    This class represent the general citizen of the model.
    Agents have the following variables:
    (a) fixed: id, gender, month of birth, qualification, family_id
    (b) variable: age, money (amount owned at any given moment), saving,
    firm_id, utility, address, distance, region_id.
    """

    # Class for Agents. Citizens of the model
    # Agents live in families, work in firms, consume
    def __init__(self, id,
                 gender,
                 age,
                 qualification,
                 money,
                 month,
                 firm_id=None,
                 family=None,
                 distance=0):

        self.id = id
        self.gender = gender
        self.age = age
        self.month = month # Birthday month
        self.qualification = qualification
        self.money = money
        self.firm_id = firm_id
        self.distance = distance
        self.family = family
        self.last_wage = None
        self.p_marriage = marriage_data.p_marriage(self)

    @property
    def address(self):
        return self.family.address

    @property
    def region_id(self):
        return self.family.region_id

    @property
    def is_minor(self):
        return self.age < 16

    @property
    def is_retired(self):
        return self.age > 70

    def grab_money(self):
        d = self.money
        self.money = 0
        return d

    @property
    def belongs_to_family(self):
        return self.family is not None

    @property
    def is_employed(self):
        return self.firm_id is not None

    @property
    def is_employable(self):
        return not self.is_retired \
            and not self.is_minor \
            and not self.is_employed

    def set_commute(self, firm):
        """Set (cache) commute according to their employer firm"""
        if firm is not None:
            self.distance = self.distance_to_firm(firm)
        else:
            self.distance = 0

    def __repr__(self):
        return 'Ag. ID: %s, %s, Qual. %s, Age: %s, Money $ %.2f, Firm: %s, Util. %.2f' % \
               (self.id, self.gender, self.qualification, self.age, self.money, self.firm_id, self.utility)

    def distance_to_firm(self, firm):
        return self.family.house.distance_to_firm(firm)
