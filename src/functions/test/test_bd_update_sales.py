import unittest, sys, os

# Configure path to import modules
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from bd_update_sales.apis import *



class TestApi(unittest.TestCase):
    
    def test_api_list(self):
        self.assertEqual(get_apis_list(['ifood', 'rappi']), ['api_ifood', 'api_rappi'])