'''
This script is responsible for getting the latest price listing for an item.
'''
import re
import logging
import requests
from currency_converter import CurrencyConverter

# set up the logger
LOGGER = logging.getLogger(__name__)
FILE_HANDLER = logging.FileHandler('all_logs.log')
FORMATTER = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
FILE_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(FILE_HANDLER)

CONVERTER = CurrencyConverter()
CURRENCY_LIST = ["INR", "USD", ""]

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
            parsed_url = "https://steamcommunity.com/market/priceoverview/?appid={}&market_hash_name={}&currency=1".format(app_id, hashname)

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

if __name__ == "__main__":
    link = "https://steamcommunity.com/market/listings/570/Exalted%20Bladeform%20Legacy"
    check_item_price_below_threshold(link, 2000)