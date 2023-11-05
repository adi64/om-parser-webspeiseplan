# -*- encoding: utf-8 -*-

import logging
from pyopenmensa.feed import LazyBuilder

LOG = logging.getLogger(__name__)
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

PRICE_ROLE_MAPPING = {
    'student': 'mitarbeiterpreisDecimal2',
    'other': 'gaestepreisDecimal2',
    'employee': 'price3Decimal2'
}

def _notes(offer):
    result = []
    nutritional_values_strings = []
    nutritional_values_format_string_mapping = {
        'nwkcalInteger': '{} kcal energy',
        'nwkjInteger': '{} kJ energy',
        'nweiweissDecimal1': '{} g protein',
        'nwfettDecimal1': '{} g fat',
        'nwfettsaeurenDecimal1': 'thereof {} g saturated fats',
        'nwkohlehydrateDecimal1': '{} g carbohydrates',
        'nwzuckerDecimal1': 'thereof {} g sugar',
        'nwsalzDecimal1': '{} g salt',
    }

    for key in nutritional_values_format_string_mapping.keys():
        if key in offer:
            nutritional_values_strings.append(nutritional_values_format_string_mapping[key].format(offer[key]))

    nutritional_values = ', '.join(nutritional_values_strings)
    
    result.append(nutritional_values)
    return result


def _prices(offer):
    result = {}
    for role, api_role in PRICE_ROLE_MAPPING.items():
        if api_role not in offer:
            continue

        price = offer[api_role]
        # When no price is set, this can be empty dict
        if isinstance(price, float) or (isinstance(price, str) and price.strip()):
            result[role] = price

    return result

def render_menu(menu):
    """Render the menu for a canteen into an OpenMensa XML feed.

    :param dict menu: the Python representation of the API JSON response
    :return: the XML feed as string
    """
    builder = LazyBuilder()

    for block in menu:
        meta = block['speiseplanAdvanced']
        meals = block['speiseplanGerichtData']
        for meal in meals:
            day = meal['speiseplanAdvancedGericht']['datum']
            name = meal['speiseplanAdvancedGericht']['gerichtname']
            category = meta['anzeigename']
            builder.addMeal(date=day,
                category=category,
                name=name,
                notes=_notes(meal['zusatzinformationen']),
                prices=_prices(meal['zusatzinformationen']),
                roles=None)

    return builder.toXMLFeed()


def render_meta(canteen, menu_feed_url):
    """Render a OpenMensa XML meta feed for a given canteen.

    :param Canteen canteen: the canteen
    :param menu_feed_url: the canteen menu URL
    :return: the XML meta feed as string
    """
    builder = LazyBuilder()

    builder.name = canteen.name
    builder.address = canteen.street
    builder.city = canteen.city

    builder.define(name='full',
                   priority='0',
                   url=menu_feed_url,
                   source=None,
                   dayOfWeek='*',
                   dayOfMonth='*',
                   hour='8-18',
                   minute='0',
                   retry='30 1')

    return builder.toXMLFeed()
