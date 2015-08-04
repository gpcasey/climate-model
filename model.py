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

    def __init__(self, type, alpha=ALPHA, beta=BETA,
                 tau_u=TAU_U, tau_s=TAU_S, ctilde=CTILDE,
                 age_middle=AGE_MIDDLE, age_old=AGE_OLD, age_max=AGE_MAX):
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

    def get_n(self):
        return self._nu, self._ns

    def get_age(self):
        return self._age

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
        # Calculations
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
    Class for the entire economy. Made up of Firms and Individuals.
    """

    def __init__(self, Time):
        """
        Initialize firms and individuals within the class.
        """
        self._firm_list = []
        self._unskill_list = []
        self._skill_list = []
        for t in range(Time):
            new_firm = Firm(0, 0, 0, 0, 0, .6)
            self._firm_list.append(new_firm)
            new_unskill = Individual(low, t)
            self._unskill_list.append(new_unskill)
            new_skill = Individual(low, t)
            self._skill_list.append(new_skill)

    def calc_aggregate(self, nu, ns):
        """
        Calculate aggregate values for an economy.
        """
        pass

    def get_aggregate(self):
        """
        Return aggregate values.
        :return:
        """

        pass

    def labor_allocation(self):
        """
        Calculate allocation of unskilled labor.
        """
        pass

    def get_omega(self):
        """
        Returns omega values for each year.
        :return:
        """


def initial(H_m, L_m, L_a, N, Y_a, Y_m):
    """
    Algorithm for determining initial prices and technology levels.
    """
    pass
