from agents import Agent
from .population import marriage_data

# Importing official Data from IBGE, 2000-2030
# NOTE: There are different DATA available for each year 2000-2030 for each State


def check_demographics(sim, birthdays, year, mortality_men, mortality_women, fertility):
    """Agent life cycles: update agent ages, deaths, and births"""
    births, deaths = [], 0
    for age, agents in birthdays.items():
        age = age + 1
        prob_mort_m = mortality_men.get_group(age)[str(year)].iloc[0]
        prob_mort_f = mortality_women.get_group(age)[str(year)].iloc[0]
        if 14 < age < 50:
            p_pregnancy = fertility.get_group(age)[str(year)].iloc[0]

        for agent in agents:
            agent.age += 1
            agent.p_marriage = marriage_data.p_marriage(agent)
            if agent.gender == 'Male':
                if sim.seed.random() < prob_mort_m:
                    die(sim, agent)
                    deaths += 1

            else:
                if 14 < age < 50:
                    child = pregnant(sim, agent, p_pregnancy)
                    if child is not None:
                        births.append(child)

                # Mortality procedures
                # Extract specific agent data to calculate mortality 'Female'
                if sim.seed.random() < prob_mort_f:
                    die(sim, agent)
                    deaths += 1
    return births, deaths


def birth(sim):
    """Similar to create agent, but just one individual"""
    age = 0
    qualification = int(sim.seed.gammavariate(3, 3))
    qualification = [qualification if qualification < 21 else 20][0]
    money = sim.seed.randrange(20, 40)
    month = sim.seed.randrange(1, 13, 1)
    gender = sim.seed.choice(['Male', 'Female'])
    sim.total_pop += 1
    a = Agent((sim.total_pop - 1), gender, age, qualification, money, month)
    return a


def pregnant(sim, agent, p_pregnancy):
    """An agent is born"""
    if sim.seed.random() < p_pregnancy:
        child = birth(sim)
        agent.family.add_agent(child)
        sim.agents[child.id] = child
        sim.update_pop(None, child.region_id)
        return child


def die(sim, agent):
    """An agent dies"""
    sim.grave.append(agent)

    # This makes the house vacant if all members of a given family have passed
    if agent.family.num_members == 1:
        # Save houses of empty family
        id = agent.family.id
        inheritance = [h for h in sim.houses.values() if h.owner_id == id]
        to_empty = [h for h in sim.houses.values() if h.family_id == id]
        for each in to_empty:
            each.family_id = None
            each.rent_data = None
        # Make houses vacant
        for h in inheritance:
            h.owner_id = None
            agent.family.owned_houses.remove(h)

        # Eliminate families with no members
        id = agent.family.id
        del sim.families[id]
        unassigned_houses = [h for h in sim.houses.values() if h.owner_id == id]
        assert len(unassigned_houses) == 0

        savings = agent.family.grab_savings(sim.central, sim.clock.year, sim.clock.months)
        relatives = [sim.families[i] for i in agent.family.relatives if i in sim.families]

        # Redistribute houses, debt, and savings of empty family
        if relatives:
            # Choose a member to get house/houses and debt, if any
            if inheritance:
                lucky_ones = sim.seed.choices(relatives, k=len(inheritance))
                # Most expensive house last. Will pop for the luckiest, so,
                # who gets the most expensive house, also gets the debt, if any
                inheritance.sort(key=lambda h: h.price, reverse=False)
                debtor = lucky_ones.pop()
                sim.generator.randomly_assign_houses(inheritance.pop(), debtor)
                # If we still have other houses and other relatives, assign randomly
                if inheritance and lucky_ones:
                    sim.generator.randomly_assign_houses(inheritance, lucky_ones)
                # If we have just more houses, give them all to the survivor
                elif inheritance:
                    sim.generator.randomly_assign_houses(inheritance, debtor)
            else:
                debtor = sim.seed.choice(relatives)

            # Distribute savings equally
            savings_per_relative = savings/len(relatives)
            for f in relatives:
                f.update_balance(savings_per_relative)

            # Distribute debt
            if id in sim.central.loans:
                loans = sim.central.loans.pop(id)
                sim.central.loans[debtor.id] = loans

        else:
            # Assign randomly
            sim.generator.randomly_assign_houses(inheritance, sim.families.values())

            # Delete debt
            if id in sim.central.loans:
                del sim.central.loans[id]
    else:
        agent.family.remove_agent(agent)

    if agent.is_employed:
        sim.firms[agent.firm_id].obit(agent)
    if agent.family is not None:
        sim.update_pop(agent.region_id, None)

    a_id = agent.id
    del sim.agents[a_id]

