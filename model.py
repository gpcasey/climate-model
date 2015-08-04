__user__ = 'Greg'
__project__ = 'Checking'

import math

# Constants
ALPHA = .3
BETA = .3
EPSILON = .6
TAU_U = .15
TAU_S = .15 * 1.3
CTILDE = .1
TOLW = .02
AGE_MIDDLE = 1
AGE_OLD = 2
AGE_MAX = 2
NVECTOR = [n / 500.0 for n in range(0, 1200)]


class Firm:
    """
    Describes behavior of aggregate firm.
    """

    def __init__(self, Hm, Lm, La, Am, Aa, epsilon=EPSILON):
        """
        Initialize firm.
        """
        self._epsilon = epsilon
        self._Hm = Hm
        self._Lm = Lm
        self._La = La
        self._Aa = Aa
        self._Am = Am
        self._Ya = Aa * La
        self._Ym = Am * Hm ** self._epsilon * Lm ** (1 - self._epsilon)
        self._wu = Am * (1 - self._epsilon) * Hm ** self._epsilon * Lm ** (-1 * self._epsilon)
        self._ws = Am * self._epsilon * Hm ** (self._epsilon - 1) * Lm ** (1 - self._epsilon)
        self._pa = self._wu / self._Aa
        self._Yt = self._Ym + self._pa * self._Ya

    def update(self, Hm, Lm, La, Am, Aa):
        """
        Update production based on new inputs.
        """
        self._Hm = Hm
        self._Lm = Lm
        self._La = La
        self._Aa = Aa
        self._Am = Am
        self._Ya = Aa * La
        self._Ym = Am * Hm ** self._epsilon * Lm ** (1 - self._epsilon)
        self._wu = Am * (1 - self._epsilon) * Hm ** self._epsilon * Lm ** (-1 * self._epsilon)
        self._ws = self._epsilon * Am * (Hm ** (self._epsilon - 1)) * (Lm ** (1 - self._epsilon))
        self._pa = self._wu / self._Aa
        self._Yt = self._Ym + self._pa * self._Ya

    def get_labor(self):
        """
        return labor aggregates.
        """
        return self._Hm, self._Lm, self._La

    def get_tech(self):
        """
        return tech levels
        """
        return self._Am, self._Aa

    def get_prices(self):
        """
        return prices and wages.
        """
        return self._ws, self._wu, self._pa

    def get_output(self):
        """
        Return output by sector and total.
        """
        return self._Yt, self._Ym, self._Ya

    def copy(self):
        """
        Make a copy of the firm.
        """
        new_firm = Firm(self._Hm, self._Lm, self._La, self._Am, self._Aa, self._epsilon)
        return new_firm




class Individual:
    """
    Describes behavior of individual.
    """

    def __init__(self, type, alpha = ALPHA, beta = BETA,
                 tau_u = TAU_U, tau_s = TAU_S, ctilde = CTILDE,
                 age_middle = AGE_MIDDLE, age_old = AGE_OLD, age_max = AGE_MAX,
                 size = 1):
        """
        Define constants for a person. Mutable objects set to 0.
        """
        self._skill = type
        self._age = 0
        self._ns = 0
        self._nu = 0
        self._alpha = alpha
        self._beta = beta
        self._tau_u = tau_u
        self._tau_s = tau_s
        self._ctilde = ctilde
        self._age_middle = age_middle
        self._age_old = age_old
        self._age_max = age_max
        self._size = size

    def copy(self):
        new_indiv = Individual(self._skill, self._alpha, self._beta,
                               self._tau_u, self._tau_s, self._ctilde,
                               self._age_middle, self._age_old, self._age_max)
        new_indiv.update_n(self._nu, self._ns)
        new_indiv.update_age(self._age)
        return new_indiv

    def update_n(self, nu, ns):
        self._ns = ns
        self._nu = nu

    def update_age(self, input):
        self._age = input

    def update_size(self, input):
        self._size = input

    def get_n(self):
        return self._nu, self._ns

    def get_age(self):
        return self._age

    def get_size(self):
        return self._size

    def utility(self, wage, price, cm, ca, omegau, omegas):
        """
        Single period utility.
        """
        age = self._age
        # Check basic conditions for logs
        if (ca <= self._ctilde) or (cm <= 0):
            return float("-inf")

        # Normal Calculations
        if age < self._age_middle:
            return 0
        elif age < self._age_old:
            if (wage * (1 - (self._tau_u * self._nu + self._tau_s * self._ns))) < ((cm + price * ca) - .001): #adjustment for floating point.
                return float("-inf")
            elif max(self._ns, self._nu) <= 0:
                return float("-inf")
            else:
                return (self._alpha * math.log(cm) + self._beta * math.log(ca - self._ctilde)
                        + (1 - self._alpha - self._beta) * math.log(omegau * self._nu + omegas * self._ns))
        elif age >= self._age_old and age <= self._age_max:
            if wage < cm + price * ca - .001:
                return float("-inf")
            else:
                return self._alpha * math.log(cm) + self._beta * math.log(ca - self._ctilde)
        else:
            return None

    def get_consumption(self, wage, price):
        """
        Get optimal consumption conditional on prices and fertility.
        """
        if self._age < self._age_middle:
            return 0, 0
        else:
            if (self._age >= self._age_middle) and (self._age < self._age_old):
                working_time = (1 - self._tau_u * self._nu - self._tau_s * self._ns)
            elif self._age >= self._age_old:
                working_time = 1
            else:
                assert False, "age error"
            ratio = (self._beta / self._alpha)
            numerator = ratio * (working_time * wage - price * self._ctilde)
            denominator = (1 + ratio)
            c_m = numerator / denominator
            c_a = (wage * working_time - c_m) / price
            return c_m, c_a

    def get_gamma(self):
        return self._ns * self._tau_s + self._nu * self._tau_u

    def work(self):
        return ((self._age >= self._age_middle) and (self._age <= self._age_max))

    def maximize_n(self, wages, prices, omegau, omegas, last_ratio, tolw=TOLW, nvector=NVECTOR):
        """
        Choose maximum number of children.
        First check taus against omega.
        With both types of children, keep ratio from last iteration.
        :type self: object
        """
        new_indiv = self.copy()
        if (omegas / omegau) > ((self._tau_s / self._tau_u) + tolw):
            final_n = (0, 0)
            best = float("-inf")
            for n in nvector:
                new_indiv.update_n(0, n)
                utils = sum([new_indiv.utility(wages[i], prices[i], new_indiv.get_consumption(wages[i], prices[i])[0],
                                          new_indiv.get_consumption(wages[i], prices[i])[1], omegau, omegas)
                             for i in range(len(prices))])
                if utils > best:
                    final_n = (0, n)
                    best = utils

        elif (omegas / omegau) < ((self._tau_s / self._tau_u) - tolw):
            final_n = (0, 0)
            best = float("-inf")
            for n in nvector:
                new_indiv.update_n(n, 0)
                utils = sum([new_indiv.utility(wages[i], prices[i], new_indiv.get_consumption(wages[i], prices[i])[0],
                                          new_indiv.get_consumption(wages[i], prices[i])[1], omegau, omegas)
                             for i in range(len(prices))])
                if utils > best:
                    final_n = (n, 0)
                    best = utils

        elif ((omegas / omegau) <= ((self._tau_s / self._tau_u) + tolw)
              and (omegas / omegau) >= ((self._tau_s / self._tau_u) - tolw)):
            final_n = (0, 0)
            best = float("-inf")
            for nlow in nvector:
                nhigh = nlow * last_ratio
                new_indiv.update_n(nlow, nhigh)
                utils = sum([new_indiv.utility(wages[i], prices[i], new_indiv.get_consumption(wages[i], prices[i])[0],
                                          new_indiv.get_consumption(wages[i], prices[i])[1], omegau, omegas)
                             for i in range(len(prices))])
                if utils > best:
                    final_n = (nlow, nhigh)
                    best = utils
        else:
            assert False, "No condition met"

        assert final_n[0] >= 0 and final_n[1] >= 0
        assert max(final_n) > 0
        assert max(final_n) != max(nvector)

        return final_n


class Economy:
    """
    Class for the entire economy.
    """

    def __init__(self, start_time, end_time, bigB = B, delta = DELTA, eta_m = ETA_M, eta_a = ETA_A):
        """
        Initialize firms and individuals within the class.
        """
        self._firm_dict = {}
        self._indiv_dict = {}
        self._pop_dict = {}
        self._supply_dict = {}
        self._start_time = start_time
        self._end_time = end_time
        self._bigB = bigB
        self._delta = delta
        self._eta_m = eta_m
        self._eta_a = eta_a

    def add_indivs(self, indivs, year):
        low_skill, high_skill = indivs
        self._indiv_dict[year] = (low_skill, high_skill)

    def add_firm(self, firm, year):
        self._firm_dict[year] = firm

    def get_indivs(self):
        return self._indiv_dict

    def get_firms(self):
        return self._firm_dict

    def add_all_indivs(self, in_ns, in_nu, year1, year2):
        """
        A shortcut for adding individuals in all years.
        Useful to initializing in loop.
        """
        for t in range(year1, year2 + 1):
            new_low = Individual("low")
            new_low.update_n(in_nu, in_ns)
            new_high = Individual("high")
            new_high.update_n(in_nu, in_ns)
            self.add_indivs((new_low, new_high), t)

    def labor_allocation(self, l_tilde, N, Aa, ctilde = CTILDE, beta = BETA, alpha = ALPHA, epsilon = EPSILON):
        """
        Calculate allocation of unskilled labor.
        """
        ratio = (beta / alpha) * (1 - epsilon)
        frac = ratio / (1 + ratio)
        l_man = frac * (l_tilde - ((N / Aa) * ctilde))
        return l_man


    def build_aggregate(self):
        """
        Calculate aggregate values for an economy.
        Also overwrites existing values.
        """
        for t in range(self._start_time, self._end_time + 1):
            H = 0
            L = 0
            H_tilde = 0
            L_tilde = 0
            for generation, individuals in self._indiv_dict.iteritems():
                low_skill, high_skill = individuals
                for person in [low_skill, high_skill]:
                    person.update_age(t - generation)
                    if person.get_type = "low":
                        L += person.work()
                        L_tilde += person.work() * (1 - person.get_gamma())
                    elif person.get_type = "high":
                        H += person.work()
                        H_tilde += person.work() * (1 - person.get_gamma())
                    else:
                        assert False, "No Person Type"
            self._pop_dict[t] = (L, H)
            self._supply_dict[t] = (L_tilde, H_tilde)



    def tech_growth(self, ratio):
        """
        Technology growth rate calculation
        """
        gpt = B * ratio ** delta
        return self._eta_a * gpt, self._eta_m * gpt



    def build_firms(self, year1, year2):
        """
        populates firms dictionary between two given years.
        """

        for t in range(year1, year2 + 1):
            new_Aa = self.tech_growth()


    def update_sizes(self, year1, year2):
        """
        update all sizes.
        """
        for t in range(year1, year2  + 1):
            low_skill, high_skill = self._indiv_dict[t]
            for person in [low_skill, high_skill]:
                p_low, p_high = self._indiv_dict[t - AGE_BIRTH]
                if person.get_type() = "low"
                    new_size = p_low.get_size() * p_low.get_n()[0] + p_high.get_size() * p_high.get_n()[0]
                elif person.get_type() = "high":
                    new_size = p_low.get_size() * p_low.get_n()[1] + p_high.get_size() * p_high.get_n()[1]
                person.update_size(new_size)


    def get_pop(self, year):
        """
        Return aggregate values.
        :return:
        """
        return self._pop_dict[year]

    def get_supply(self, year):
        """
        Return aggregate values.
        :return:
        """
        return self._supply_dict[year]


    def get_omega(self, year):
        """
        Returns omega values for each year.
        """
        out_u = 0
        out_s = 0
        for t in range(year + 20, year + 40 + 1):
            s, u, p = self._firm_dict[t].get_prices()
            out_u += u
            out_s += s
        return out_u, out_s


def initial(H_m, L_m, L_a, N, Y_a, Y_m):
    """
    Algorithm for determining initial prices and technology levels.
    """
    pass


def big_loop():
    """
    :return:
    """

    # initialize economy.

    # difference = 1 million pesos

    # while difference > blah blah blah

        # update sizes

        # update aggregates

        # make optimal decisions

        # generate new guesses

        # calc difference

    pass
