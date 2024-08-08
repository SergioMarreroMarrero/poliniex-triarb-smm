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
                  get_price_for_t_pair)
from config import POLONIEX_CONFIG, PATH_TO_STRUCTURED_TRIANGULAR_PAIRS
import json
import time

if __name__ == '__main__':

    # Step 0
    # get_coin_tickers
    tickers = PoloniexTradeableTickers(config=POLONIEX_CONFIG)()

    # Step 1
    tap = AvailableTriangleArbitragePairs(list_of_pairs=list(map(lambda x: tuple(x.split('_')), tickers)))
    structured_triangular_pairs = tap.get_all_triangles_given_a_list_of_coins(dict_format=True)
    tap.dump(structured_triangular_pairs=structured_triangular_pairs, path_to_structured_triangular_pairs=PATH_TO_STRUCTURED_TRIANGULAR_PAIRS)
    # Step 2
    with open(PATH_TO_STRUCTURED_TRIANGULAR_PAIRS, 'r') as json_file:
        structured_triangular_pairs = json.load(json_file)

    # Get Latest Surface Prices
    prices = PoloniexTradeablePrices(config=POLONIEX_CONFIG)()



    for t_pair in structured_triangular_pairs:
        time.sleep(0.3)
        prices_dict = get_price_for_t_pair(t_pair, prices)
        print(prices_dict)



