__author__ = 'Greg'
import model
import math
from decimal import Decimal
# Constants
TOLW = .02
NVECTOR = [n / 100.0 for n in range(0, 1000)]


def check_small_indiv():
    """
    Check small methods for Individual class.
    :return: Test Results.
    """
    test_indiv = model.Individual("L", .4, .3,
                                  .15, 1.3 * .15, .1,
                                  1, 2, 2)

    test_indiv.update_n(2, 1)
    if not test_indiv.get_n() == (2, 1):
        print "SMALL1", test_indiv.get_n()
    test_indiv.update_age(40)
    if not test_indiv.get_age() == 40:
        print "SMALL2", test_indiv.get_age()

    test_indivB = test_indiv.copy()
    if not test_indivB.get_n() == (2, 1):
        print "SMALL3", test_indivB.get_n()
    if not test_indivB.get_age() == 40:
        print "SMALL4", test_indivB.get_age()
    if not test_indivB._alpha == .4:
        print "SMALL5", test_indivB._alpha
    if not test_indivB._beta == .3:
        print "SMALL6", test_indivB._beta


def check_utility():
    """
    :return: test results
    """
    test_indiv = model.Individual("L", .4, .3,
                                  .15, 1.3 * .15, .1,
                                  1, 2, 2)
    test_indiv.update_n(1, 1)
    test_indiv.update_age(test_indiv._age_middle)
    #basic tests for log utility
    if not test_indiv.utility(1, .5, 1, 0, 2, 1) == float("-inf"):
        print  "BASIC1", test_indiv.utility(1, .5, 1, 0, 2, 1)
    if not test_indiv.utility(1, .5, 0, 1, 2, 1) == float("-inf"):
        print "BASIC2", test_indiv.utility(1, .5, 0, 1, 2, 1)
    if not test_indiv.utility(1, .5, 0, test_indiv._ctilde - .01, 2, 1) == float("-inf"):
        print "BASIC3", test_indiv.utility(1, .5, .1, test_indiv._ctilde, 2, 1)
    test_indiv.update_n(0, 0)
    if not test_indiv.utility(100, .1, 4, 4, 1, 2) == float("-inf"):
        print "BASIC4", test_indiv.utility(100, .1, 4, 4, 1, 2)
        print "kids: ", (test_indiv._nu, test_indiv._ns), test_indiv._age
        # note:  no children --> -inf

    #budget constraint tests
    test_indiv.update_n(1, 1)
    if not test_indiv.utility(1.2, .1, 1, 1, 1, 2) == float("-inf"):
        print "BC1", test_indiv.utility(1.2, .1, 1, 1, 1, 2)
    test_indiv.update_age(test_indiv._age_old)
    if not test_indiv.utility(1.2, .1, 1, 1, 1, 2) > float("-inf"):
        print "BC2", test_indiv.utility(1.2, .1, 1, 1, 1, 2)
        # note:  this is the same as BC1, but is feasible when not raising children.
    if not test_indiv.utility(1.2, .1, 1, 3, 1, 2) == float("-inf"):
        print "BC3", test_indiv.utility(1.2, .1, 1, 1, 1, 2)
        # note:  this is almost the same as BC2, but adds just enough to make it infeasible
    if not test_indiv.utility(1.2, .1, 1, 2, 1, 2) > float("-inf"):
        print "BC4", test_indiv.utility(1.2, .1, 1, 1, 1, 2)
        # note:  On the BC, should be positive utility.

    #Accuracy tests
    test_indiv.update_age(test_indiv._age_middle)
    test_indiv.update_n(math.e / 2.0, math.e / 2.0)
    if not test_indiv.utility(100, 1, math.e, math.e + test_indiv._ctilde, 1, 1) == 1:
        print "ACC1", test_indiv.utility(100, 1, math.e, math.e + test_indiv._ctilde, 1, 1)
    test_indiv.update_n(math.e / 4.0, math.e)
    if not test_indiv.utility(100, 1, math.e, math.e + test_indiv._ctilde, 2, .5) == 1:
        print "ACC2", test_indiv.utility(100, 1, 1, 1 + test_indiv._ctilde, 2, .5)
        #test match between costs and output for different types of children.

    test_indiv.update_age(test_indiv._age_old)
    if not test_indiv.utility(100, 1, math.e, math.e + test_indiv._ctilde, 1, 1) == 1 * (test_indiv._alpha + test_indiv._beta):
        print "ACC3", test_indiv.utility(100, 1, math.e, math.e + test_indiv._ctilde, 1, 1)
        # note:  compare wth ACC1. This shows correct update for being older.



def check_get_consumption():
    """
    :return: Test Results.
    """
    test_indiv = model.Individual("L", .4, .3,
                                  .15, 1.3 * .15, .1,
                                  1, 2, 2)
    if not test_indiv.get_consumption(2, 1) == (0, 0):
        print "GC1", test_indiv.get_consumption(1, 1)
        #note:  too young for consumption.

    test_indiv.update_age(test_indiv._age_middle)
    test_indiv.update_n(2, 1)
    if not ((round(test_indiv.get_consumption(2, 1)[0], 4), round(test_indiv.get_consumption(2, 1)[1], 4))
                == (.39, .62)):
        print "GC2", test_indiv.get_consumption(2, 1)

    test_indiv.update_age(test_indiv._age_old)
    if not ((round(test_indiv.get_consumption(2, 1)[0], 4), round(test_indiv.get_consumption(2, 1)[1], 4))
            == (round(.8143, 4), round(1.1857, 4))):
        print "GC3", test_indiv.get_consumption(2, 1)
    test_indiv.update_n(1, 1)
    if not ((round(test_indiv.get_consumption(2, 1)[0], 4), round(test_indiv.get_consumption(2, 1)[1], 4))
            == (round(.8143, 4), round(1.1857, 4))):
        print "GC4", test_indiv.get_consumption(2, 1)
        #note:  changing children shouldnt matter.

def check_maximize():
    """
    :return: test_results
    """
    #note:  can only round to as many decimal places as nvector will allow.
    test_indiv = model.Individual("L", .4, .3,
                                  .15, 1.3 * .15, 0,
                                  1, 2, 2)


    # Single Period Tests, no ctilde
    test_indiv.update_age(test_indiv._age_middle)
    answer_low, answer_high = test_indiv.maximize_n([2], [1], 4, 1, .75, .05)
    if (not (round(answer_low, 2), round(answer_high, 2))
        == (round(.3 / .15, 2), 0)):
        print "MAX1", (round(answer_low, 2), round(answer_high, 2))
        # note: 1 period case. only low skill.

    answer_low, answer_high = test_indiv.maximize_n([2], [1], 1, 4, .75, .05)
    if (not (round(answer_low, 2), round(answer_high, 2))
        == (0, round(.3 / (.15*1.3), 2))):
        print "MAX2", (round(answer_low, 2), round(answer_high, 2)), (0, round(.3 / (.15*1.3), 2))
        # note: 1 period case. only low skill.

    answer_low, answer_high = test_indiv.maximize_n([2], [1], 2 * test_indiv._tau_u, 2 * test_indiv._tau_s + .01, .75, .05)
    low = (.3 / (.15 + .15*1.3*.75))
    high = .75 * low
    if (not (Decimal(answer_low), Decimal(answer_high))
        == (Decimal(low), Decimal(high))):
        print "MAX3", (Decimal(answer_low), Decimal(answer_high)), (Decimal(low), Decimal(high))
        # note: 1 period case. both skills.


    # Multi-Period Tests, no ctilde
    answer_low, answer_high = test_indiv.maximize_n([2, 4], [1, .5], 4, 1, .75, .05)
    if (not (round(answer_low, 2), round(answer_high, 2))
        == (round(.3 / .15, 4), 0)):
        print "MAX4", (round(answer_low, 2), round(answer_high, 2))
        # note: 1 period case. only low skill.

    answer_low, answer_high = test_indiv.maximize_n([2, 12], [.5, 1], 1, 4, .75, .05)
    if (not (round(answer_low, 2), round(answer_high, 2))
        == (0, round(.3 / (.15*1.3), 2))):
        print "MAX5", (round(answer_low, 2), round(answer_high, 2)), (0, round(.3 / (.15*1.3), 2))
        # note: 1 period case. only low skill.

    answer_low, answer_high = test_indiv.maximize_n([4, 7], [1, 3], 2 * test_indiv._tau_u, 2 * test_indiv._tau_s + .01, .75, .05)
    low = (.3 / (.15 + .15*1.3*.75))
    high = .75 * low
    if (not (Decimal(answer_low), Decimal(answer_high))
        == (Decimal(low), Decimal(high))):
        print "MAX6", (Decimal(answer_low), Decimal(answer_high)), (Decimal(low), Decimal(high))
        # note: 1 period case. both skills.



print "****************CHECK SMALL*****************"
check_small_indiv()

print "************ CHECK UTILITY *******************"
check_utility()

print "***********CHECK GET_CONSUMPTION *************"
check_get_consumption()

print "***********CHECK MAXIMIZE *************"
check_maximize()

