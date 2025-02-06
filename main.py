# STEP 0: Gather correct coins
"""
    STEP 0: Finding coins which can be traded
    Exchange: Poloniex
    https://api-docs.poloniex.com/futures
    https://api-docs.poloniex.com/spot
"""
# from pprint import pprint
# from curso import structure_triangular_pairs
from core import (PoloniexTradeableTickers,
                  PoloniexTradeablePrices,
                  AvailableTriangleArbitragePairs,
                  get_price_for_t_pair, get_triangle)
from config import POLONIEX_CONFIG, PATH_TO_STRUCTURED_TRIANGULAR_PAIRS
import json
import time




if __name__ == '__main__':

    # Step 0
    # get_coin_tickers
    tickers = PoloniexTradeableTickers(config=POLONIEX_CONFIG)()
    l = PoloniexTradeableTickers(config=POLONIEX_CONFIG).extract()
    from pprint import pprint
    pprint(l.json()[0])
    t_tickers = list(map(lambda x: tuple(x.split('_')), tickers))

    # Step 1
    tap = AvailableTriangleArbitragePairs(list_of_pairs=t_tickers)
    structured_triangular_pairs = tap.get_all_triangles_given_a_list_of_coins(dict_format=True)
    tap.dump(structured_triangular_pairs=structured_triangular_pairs, path_to_structured_triangular_pairs=PATH_TO_STRUCTURED_TRIANGULAR_PAIRS)
    # Step 2
    with open(PATH_TO_STRUCTURED_TRIANGULAR_PAIRS, 'r') as json_file:
        structured_triangular_pairs = json.load(json_file)

    # Get Latest Surface Prices
    prices = PoloniexTradeablePrices(config=POLONIEX_CONFIG)()
    # prices[0]

    #
    t_pair = get_triangle(structured_triangular_pairs)
    # Set Variables
    min_surface_rate = 0 # threshold
    surface_dict = {}
    contract_2 = ""
    contract_3 = ""
    direction_trade_1 = ""
    direction_trade_2 = ""
    direction_trade_3 = ""



