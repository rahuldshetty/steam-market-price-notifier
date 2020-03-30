#!/usr/bin/python
'''
This script is responsible for getting the latest price listing for an item.
'''
import re
import requests
from currency_converter import CurrencyConverter
from utils import *

CONVERTER = CurrencyConverter()
CURRENCY_LIST = sorted(list(CONVERTER.currencies))

STEAM_LINK = "https://steamcommunity.com/market/priceoverview/?appid={}&market_hash_name={}&currency=1"

def check_item_price_below_threshold(link, threshold=0.0, currency="INR"):
    '''
    Checks if the item price is below the given threshold
    '''
    # parse the url to obtain AppID and Market HashName
    lists = re.findall('[0-9]+', link)
    try:
        if lists != []:
            app_id = lists[0]
            hashname = link.split('/')[-1]
            parsed_url = STEAM_LINK.format(app_id, hashname)

            # make a get request to obtain the price listing
            response = requests.get(parsed_url)
            response_json = response.json()

            # get the lowest price value
            lowest_price = re.sub('[^0-9.]', '', response_json['lowest_price'])
            converted_value = CONVERTER.convert(lowest_price, "USD", currency)

            # check if the threshold is 0 or not
            if threshold == 0.0:
                return True
            else:
                return converted_value <= threshold
        else:
            LOGGER.error("No AppID found in link - %s", link)
            return None
    except Exception as error:
        LOGGER.error("Exception - %s", error)
        return None

def get_current_item_low_price(link, currency="INR"):
    '''
    This method returns the lowest price of an item.
    '''
    lists = re.findall('[0-9]+', link)
    try:
        if lists != []:
            app_id = lists[0]
            hashname = link.split('/')[-1]
            parsed_url = STEAM_LINK.format(
                app_id,
                hashname
            )

            # make a get request to obtain the price listing
            response = requests.get(parsed_url)
            response_json = response.json()

            # get the lowest price value
            lowest_price = re.sub('[^0-9.]', '', response_json['lowest_price'])
            converted_value = CONVERTER.convert(lowest_price, "USD", currency)

            return round(converted_value, 2)
        else:
            LOGGER.error("No AppID found in link - %s", link)
            return None
    except Exception as error:
        LOGGER.error("Exception - %s", error)
        return None

if __name__ == "__main__":
    link = "https://steamcommunity.com/market/listings/570/Exalted%20Bladeform%20Legacy"
    check_item_price_below_threshold(link, 2000)