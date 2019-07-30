class LaborMarket():
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

    def assign_post(self, unemployment, params):
        """Rank positions by wage and rank employees by qualifications
        Make a match """
        pct_distance_hiring = params['PCT_DISTANCE_HIRING']
        tax_consumption = params['TAX_CONSUMPTION']
        ignore_unemployment = params['WAGE_IGNORE_UNEMPLOYMENT']
        hiring_sample_size = int(round(params['HIRING_SAMPLE_SIZE']))

        self.seed.shuffle(self.candidates)

        if len(self.candidates) >= 2:
            split = int(len(self.candidates) * (1 - pct_distance_hiring))
            by_qual = self.candidates[0:split]
            by_dist = self.candidates[split:]
        else:
            return

        self.available_postings.sort(key=lambda f: f.wage_base(unemployment, tax_consumption, ignore_unemployment), reverse=True)
        by_qual.sort(key=lambda c: c.qualification, reverse=False)

        # Choosing by qualification
        for firm, candidate in zip(self.available_postings[0::2], by_qual):
            self.apply_assign(candidate, firm)

        for firm in self.available_postings[1::2]:
            if not by_dist:
                break

            # sample candidates
            candidates = self.seed.sample(by_dist, min(len(by_dist), hiring_sample_size))
            # Choosing by distance
            chosen_candidate = fast_closest(candidates, firm)
            by_dist.remove(chosen_candidate)
            self.apply_assign(chosen_candidate, firm)

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
