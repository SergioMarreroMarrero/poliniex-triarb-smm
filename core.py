from abc import ABC, abstractmethod
import requests
from collections import Counter
import json
import os

class APIResponseHandler(ABC):

    def __call__(self, *args, **kwargs):

        response = self.extract(*args, **kwargs)
        if response.status_code == 200:
            obj = self.unroll(response)
            return obj

    @abstractmethod
    def extract(self, *args, **kwargs):
        pass

    @abstractmethod
    def unroll(self, response):
        pass


class PoloniexTradeableTickers(APIResponseHandler):
    def __init__(self, config):
        self.config = config

    def __call__(self):
        response = self.extract()
        if response.status_code == 200:
            return self.unroll(response)


    def extract(self):
        response = requests.get(self.config['COINS_URL'])
        return response

    def unroll(self, response):
        json_obj = response.json()
        coin_list = []
        for coin in json_obj:
            if coin['state'] == self.config['TRADEABLE_COIN_STATE']:
                coin_list.append(coin['symbol'])
        return coin_list


class PoloniexTradeablePrices(APIResponseHandler):
    def __init__(self, config):
        self.config = config

    def extract(self):
        response = requests.get(self.config['COIN_PRICE_URL'])
        return response

    def unroll(self, response):
        return response.json()


class AvailableTriangleArbitragePairs:

    def __init__(self, list_of_pairs):
        self.list_of_pairs = list_of_pairs

    def _get_b_candidates_given_a_pair(self, a_pair):
        """
        Given a pair ('BTC', 'USDT') find all choices in dex pairs to build a triangle
        i.e. given ('BTC', 'USDT') find [('BTC', 'ETH'), ('BTC', 'ADA'), ('ADA', 'USDT')...]
        :param a_pair:
        :return:
        """
        base_coin, quote_coin = a_pair[0], a_pair[1]
        list_of_related_group = []
        for pair in self.list_of_pairs:
            if (base_coin in pair) or (quote_coin in pair):
                list_of_related_group.append(pair)

        return list_of_related_group

    def _close_triangle(self, triangle):
        """
        Given a pair find the third element to have a triangle group
        i.e. [('BTC', 'USDT'), ('BTC', 'ETH')] -> ('ETH', 'USDT')
        :param triangle:
        :return:
        """
        c_group = Counter([coin for pair in triangle for coin in pair])
        missing_pair = []
        for k, c in c_group.items():
            if c == 1:
                missing_pair.append(k)
        base_coin, quote_coin = missing_pair[0], missing_pair[1]
        for pair in self.list_of_pairs:
            if (base_coin in pair) and (quote_coin in pair):
                triangle.append(pair)
                triangle.append(set([coin for pair in triangle for coin in pair]))
                return triangle
        return None

    def _get_triangles_given_a_pair(self, a_pair):
        """
        Given a pair find al triangle arbitrage available
        :param a_pair:
        :return:
        """
        list_of_related_group_to_pair_coin = self._get_b_candidates_given_a_pair(a_pair)
        list_of_all_triangles_related_to_a_pair = []
        for b_pair in list_of_related_group_to_pair_coin:
            if a_pair == b_pair:
                continue
            triangle_ab = [a_pair, b_pair]
            triangle_coins = self._close_triangle(triangle_ab)
            if triangle_coins is not None:
                # the triangle is closed
                list_of_all_triangles_related_to_a_pair.append(triangle_coins)

        return list_of_all_triangles_related_to_a_pair

    def get_all_triangles_given_a_list_of_coins(self, list_of_pairs=None, dict_format=False):
        """
        Given a list of all tradeable pairs find all possible arbitrage triangles
        :return:
        """

        def _remove_duplicated_triangles(list_of_triangles):
            clean_list_of_triangles = []
            for new_triangle in list_of_triangles:
                duplicated = any([True for clean_triangle in clean_list_of_triangles if new_triangle[3] == clean_triangle[3]])
                if not duplicated:
                    clean_list_of_triangles.append(new_triangle)
            return clean_list_of_triangles

        def _format_triangles(list_of_triangles):
            def _format_single_triangle(triangle):
                return {
                    "a_base": triangle[0][0],
                    "b_base": triangle[1][0],
                    "c_base": triangle[2][0],
                    "a_quote": triangle[0][1],
                    "b_quote": triangle[1][1],
                    "c_quote": triangle[2][1],
                    "pair_a": '_'.join(triangle[0]),
                    "pair_b": '_'.join(triangle[1]),
                    "pair_c": '_'.join(triangle[2]),
                    "combined": f"{'_'.join(triangle[0])},{'_'.join(triangle[1])},{'_'.join(triangle[2])}"
                }

            return [_format_single_triangle(triangle) for triangle in list_of_triangles]

        list_of_pairs = self.list_of_pairs if list_of_pairs is None else list_of_pairs
        assert type(list_of_pairs) is list, 'list_of_pairs debe ser una lista'
        all_triangles = []
        print('Iterating over all possile triangles...')
        for a_pair in self.list_of_pairs:
            # print(a_pair)
            a_pair_triangles = self._get_triangles_given_a_pair(a_pair)
            if len(a_pair_triangles) > 0:
                all_triangles.extend(a_pair_triangles)

        clean_triangles = _remove_duplicated_triangles(all_triangles)
        return clean_triangles if not dict_format else _format_triangles(clean_triangles)

    @staticmethod
    def dump(structured_triangular_pairs, path_to_structured_triangular_pairs):

        directory = os.path.dirname(path_to_structured_triangular_pairs)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(path_to_structured_triangular_pairs, 'w') as json_file:
            json.dump(structured_triangular_pairs, json_file, indent=4)


def get_price_for_t_pair(t_pair, prices):
    t_pair_prices_dict = dict()
    for key, pair in t_pair.items():
        # para todos los key, value(pair) del diccionario
        if key in ['pair_a', 'pair_b', 'pair_c']:
            # si la clave es una de estas tres (el nombre de los pares BTC_USD, etc)
            for price in prices:
                # para cada diccionario de precios
                if price['symbol'] == pair:
                    # coge el precio del par en el que estemos (BTC_USD) y actualiza el diccionario con ask/bid
                    t_pair_prices_dict.update(
                        {
                            key + '_ask': price['ask'],
                            key + '_bid': price['bid']
                        }
                    )
    return t_pair_prices_dict
