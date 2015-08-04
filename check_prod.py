__author__ = 'Greg'

import model
import math

# Constants
TOLW = .02
NVECTOR = [n / 100.0 for n in range(0, 1000)]

def check_prod():
    """
    Testing package for aggregate production.
    """

    # One Firm
    test_firm = model.Firm(2, 3, 1, 4, 2, .6)
    if not test_firm.get_labor() == (2, 3, 1):
        print "PROD1", test_firm.get_labor()
    if not test_firm.get_tech() == (4, 2):
        print "PROD2", test_firm.get_tech()

    t_ws, t_wu, t_pa = test_firm.get_prices()
    if not (round(t_ws, 2), round(t_wu, 2), round(t_pa, 2)) == (2.82, 1.25, .63):
        print "PROD3", test_firm.get_prices()

    t_Yt, t_Ym, t_Ya = test_firm.get_output()
    if not (round(t_Yt, 2) , round(t_Ym, 2) , round(t_Ya, 02)) == (10.66, 9.41, 2):
        print "PROD4", test_firm.get_output()

    # Update Firm
    test_firm.update(1, 2, 3, 4, 5)
    if not test_firm.get_labor() == (1, 2, 3):
        print "PROD5", test_firm.get_labor()
    if not test_firm.get_tech() == (4, 5):
        print "PROD6", test_firm.get_tech()

    t_ws, t_wu, t_pa = test_firm.get_prices()
    if not (round(t_ws, 2), round(t_wu, 2), round(t_pa, 2)) == (3.17, 1.06, .21):
        print "PROD7", test_firm.get_prices()

    t_Yt, t_Ym, t_Ya = test_firm.get_output()
    if not (round(t_Yt, 2) , round(t_Ym, 2) , round(t_Ya, 02)) == (8.44, 5.28, 15):
        print "PROD8", test_firm.get_output()
        # got 8.45 on paper, but difference appears to be due to rounding.

    # Copy Firm
    new_firm = test_firm.copy()
    if not new_firm.get_prices() == (t_ws, t_wu, t_pa):
        print "PROD9"
    if not new_firm.get_output() == (t_Yt, t_Ym, t_Ya):
        print "PROD10"

print "*****************CHECK PRODUCTION*********************"
check_prod()


