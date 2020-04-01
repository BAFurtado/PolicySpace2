class LaborMarket:
    """
    This class makes the match among firms and prospective candidates.
    The two lists (of firms and candidates) are ordered.
    The firms that pay the highest base wage and the candidates that have the most qualification.
    Firms on top choose first.
    They randomly choose with a given probability either the candidate who lives the closest
    or the most qualified.
    Lists are emptied every month.
    """

    def __init__(self, seed):
        self.seed = seed
        self.available_postings = []
        self.candidates = []

    def add_post(self, firm):
        self.available_postings.append(firm)

    def add_candidate(self, agent):
        self.candidates.append(agent)

    @property
    def num_candidates(self):
        return len(self.candidates)

    def reset(self):
        self.available_postings = []
        self.candidates = []

    def assign_post(self, unemployment, wage_deciles, params):
        """Rank positions by wage and rank employees by qualifications
        Make a match """
        pct_distance_hiring = params['PCT_DISTANCE_HIRING']
        tax_consumption = params['TAX_CONSUMPTION']
        ignore_unemployment = params['WAGE_IGNORE_UNEMPLOYMENT']
        hiring_sample_size = int(round(params['HIRING_SAMPLE_SIZE']))

        self.seed.shuffle(self.candidates)
        if wage_deciles is not None:
            for c in self.candidates:
                if c.last_wage:
                    for i, d in enumerate(wage_deciles):
                        if d > c.last_wage:
                            break
                    p_car = params['WAGE_TO_CAR_OWNERSHIP_QUANTILES'][i]
                    c.has_car = self.seed.random() < p_car
                else:
                    c.has_car = False
        else:
            for c in self.candidates:
                c.has_car = False

        if len(self.candidates) >= 2:
            split = int(len(self.candidates) * (1 - pct_distance_hiring))
            by_qual = self.candidates[0:split]
            by_dist = self.candidates[split:]
        else:
            return

        available_postings = [(f, f.wage_base(unemployment, tax_consumption, ignore_unemployment)) for f in self.available_postings]
        available_postings.sort(key=lambda p: p[1], reverse=True)
        by_qual.sort(key=lambda c: c.qualification, reverse=False)

        # Choosing by qualification
        offers = []
        done_firms = set()
        done_cands = set()
        for firm, wage in available_postings[0::2]:
            candidates = self.seed.sample(by_qual, min(len(by_qual), hiring_sample_size))
            for c in candidates:
                transit_cost = params['PRIVATE_TRANSIT_COST'] if c.has_car else params['PUBLIC_TRANSIT_COST']
                score = wage - (c.distance_to_firm(firm) * transit_cost)
                offers.append((firm, c, c.qualification + score))
        sorted(offers, key=lambda o: o[2], reverse=True)
        for firm, candidate, _ in offers:
            if firm not in done_firms and candidate not in done_cands:
                self.apply_assign(candidate, firm)
                done_firms.add(firm)
                done_cands.add(candidate)

        offers = []
        done_firms = set()
        done_cands = set()
        for firm, wage in available_postings[1::2]:
            if not by_dist:
                break

            # sample candidates
            candidates = self.seed.sample(by_dist, min(len(by_dist), hiring_sample_size))
            for c in candidates:
                dist = c.distance_to_firm(firm)
                transit_cost = params['PRIVATE_TRANSIT_COST'] if c.has_car else params['PUBLIC_TRANSIT_COST']
                score = wage - (dist * transit_cost)
                offers.append((firm, c, score - dist))
        sorted(offers, key=lambda o: o[2], reverse=True)
        for firm, candidate, _ in offers:
            if firm not in done_firms and candidate not in done_cands:
                self.apply_assign(candidate, firm)
                done_firms.add(firm)
                done_cands.add(candidate)

        self.available_postings = []
        self.candidates = []

    def apply_assign(self, chosen, firm):
        chosen.commute = firm
        firm.add_employee(chosen)

    def look_for_jobs(self, agents):
        for agent in agents.values():
            if agent.is_employable:
                self.add_candidate(agent)

    def hire_fire(self, firms, firm_enter_freq):
        """Firms adjust their labor force based on profit"""
        for firm in firms.values():
            strategy = self.seed.random()
            # `firm_enter_freq` is the frequency firms enter the market
            if strategy > firm_enter_freq:
                if firm.profit >= 0:
                    self.add_post(firm)
                else:
                    firm.fire(self.seed)

    def __repr__(self):
        return self.available_postings, self.candidates


def fast_closest(by_dist, firm):
    return min(by_dist, key=lambda x: x.distance_to_firm(firm))
