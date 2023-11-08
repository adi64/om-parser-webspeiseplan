# -*- encoding: utf-8 -*-

import json
import logging
from collections import namedtuple
import requests

MenuParams = namedtuple('MenuParams', ('subdomain', 'location', 'token'))

LOG = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)


def _param_json(to_serialize):
    """Obtain JSON string of an object without whitespace on delimiters.

    :param dict it: The data structure to serialize
    :return: JSON string, no whitespace between separators
    """
    return json.dumps(to_serialize, separators=(',', ':'))


def download_menu(menu_params):
    """Download the menu for a specific canteen.

    :param MenuParams menu_params: the target canteen
    """
    params = {
        'location': menu_params.location,
        'token': menu_params.token,
        'model': 'menu',
    }

    headers = {
        'Referer': 'https://' + menu_params.subdomain + '.webspeiseplan.de/Menu',
        'user-agent': 'Webspeiseplan-OpenMensa-Parser/0.0.1',
    }

    url = 'https://' + menu_params.subdomain + '.webspeiseplan.de/index.php'

    response = requests.get(url, params=params, headers=headers, timeout=30)

    # urllib3 does not log response bodies - requests no longer supports it:
    # https://2.python-requests.org//en/master/api/#api-changes
    LOG.debug('Response:\n>>>>>\n%s\n<<<<<', response.text)

    response_json = response.json()

    if not response_json['success']:
        LOG.debug('Failed to get menu')
        return False

    return response.json()['content']

def download_meal_category(menu_params):
    """Download the meal categories for a specific canteen.

    :param MenuParams menu_params: the target canteen
    """
    params = {
        'location': menu_params.location,
        'token': menu_params.token,
        'model': 'mealCategory',
    }

    headers = {
        'Referer': 'https://' + menu_params.subdomain + '.webspeiseplan.de/Menu',
        'user-agent': 'Webspeiseplan-OpenMensa-Parser/0.0.1',
    }

    url = 'https://' + menu_params.subdomain + '.webspeiseplan.de/index.php'

    response = requests.get(url, params=params, headers=headers, timeout=30)

    # urllib3 does not log response bodies - requests no longer supports it:
    # https://2.python-requests.org//en/master/api/#api-changes
    LOG.debug('Response:\n>>>>>\n%s\n<<<<<', response.text)

    response_json = response.json()

    if not response_json['success']:
        LOG.debug('Failed to get meal categories')
        return False

    return response.json()['content']

def download_outlet(menu_params):
    """Download the outlet information.

    :param MenuParams menu_params:
    """
    params = {
        'token': menu_params.token,
        'model': 'outlet',
    }

    headers = {
        'Referer': 'https://' + menu_params.subdomain + '.webspeiseplan.de/InitialConfig',
        'user-agent': 'Webspeiseplan-OpenMensa-Parser/0.0.1',
    }

    url = 'https://' + menu_params.subdomain + '.webspeiseplan.de/index.php'

    response = requests.get(url, params=params, headers=headers, timeout=30)

    # urllib3 does not log response bodies - requests no longer supports it:
    # https://2.python-requests.org//en/master/api/#api-changes
    LOG.debug('Response:\n>>>>>\n%s\n<<<<<', response.text)

    response_json = response.json()

    if not response_json['success']:
        LOG.debug('Failed to get outlet')
        return False

    return response.json()['content']
