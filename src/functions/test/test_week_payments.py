import unittest, sys, os, datetime

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
sys.path.append(f'{parent}\\erp_week_payments')

from erp_week_payments.main import *


class WeekPayments(unittest.TestCase):

    today = datetime.datetime.today()

    def check_dates(self):

        for days in range(0, 7):
            self.assertTrue(in_week(self.today + datetime.timedelta(days=days)))
        
        for days in range(8,15):
            self.assertFalse(in_week(self.today + datetime.timedelta(days=days)))



if __name__ == '__main__':
    unittest.main()