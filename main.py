# STEP 0: Gather correct coins
"""
    STEP 0: Finding coins which can be traded
    Exchange: Poloniex
    https://api-docs.poloniex.com/futures
    https://api-docs.poloniex.com/spot
"""
from pprint import pprint
from core import PoloniexTradeableTickers, TriangleArbitragePairs
from config import POLONIEX_CONFIG
from curso import structure_triangular_pairs




if __name__ == '__main__':


    get_tickers = PoloniexTradeableTickers(config=POLONIEX_CONFIG)
    tickers = get_tickers()

    tap = TriangleArbitragePairs(list_of_pairs=list(map(lambda x: tuple(x.split('_')), tickers)))
    triangles = tap.get_all_triangles_given_a_list_of_coins(dict_format=True)

    # p = structure_triangular_pairs(tickers)






from pprint import pprint
pprint(p[0])
pprint(match_dict)