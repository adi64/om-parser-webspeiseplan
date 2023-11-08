# -*- encoding: utf-8 -*-

import os
import urllib.parse

import cachetools as ct

from flask import Flask, jsonify, make_response, url_for
from flask.logging import create_logger

from stw_potsdam import feed
from stw_potsdam.config import read_canteen_config
from stw_potsdam.canteen_api import MenuParams, download_menu, download_meal_category, download_outlet

from functools import partial
from collections import namedtuple

CACHE_TIMEOUT = 45 * 60

CacheKey = namedtuple('CacheKey', ('subdomain', 'location', 'token', 'model'))

# pragma pylint: disable=invalid-name

app = Flask(__name__)
app.url_map.strict_slashes = False

log = create_logger(app)

if 'BASE_URL' in os.environ:  # pragma: no cover
    base_url = urllib.parse.urlparse(os.environ.get('BASE_URL'))
    if base_url.scheme:
        app.config['PREFERRED_URL_SCHEME'] = base_url.scheme
    if base_url.netloc:
        app.config['SERVER_NAME'] = base_url.netloc
    if base_url.path:
        app.config['APPLICATION_ROOT'] = base_url.path

cache = ct.TTLCache(maxsize=30, ttl=CACHE_TIMEOUT)


def canteen_not_found(config, canteen_name):
    log.warning('Canteen %s not found', canteen_name)
    configured = ', '.join(f"'{c}'" for c in config.keys())
    message = f"Canteen '{canteen_name}' not found, available: {configured}"
    return make_response(message, 404)


def _menu_params(canteen):
    return MenuParams(subdomain=canteen.subdomain, location=canteen.location, token=canteen.token)

def _cache_key_menu(canteen):
    return CacheKey(subdomain=canteen.subdomain, location=canteen.location, token=canteen.token, model='menu')

def _cache_key_outlet(canteen):
    return CacheKey(subdomain=canteen.subdomain, location=canteen.location, token=canteen.token, model='outlet')

def _cache_key_meal_category(canteen):
    return CacheKey(subdomain=canteen.subdomain, location=canteen.location, token=canteen.token, model='meal_category')

@ct.cached(cache=cache, key=_cache_key_menu)
def get_menu(canteen):
    log.info('Downloading menu for %s', canteen)
    params = _menu_params(canteen)
    return download_menu(params)

@ct.cached(cache=cache, key=_cache_key_outlet)
def get_outlet(canteen):
    log.info('Downloading outlet for %s', canteen)
    params = _menu_params(canteen)
    return download_outlet(params)

@ct.cached(cache=cache, key=_cache_key_meal_category)
def get_meal_category(canteen):
    log.info('Downloading meal categories for %s', canteen)
    params = _menu_params(canteen)
    return download_meal_category(params)

def _canteen_feed_xml(xml):
    response = make_response(xml)
    response.mimetype = 'text/xml'
    return response


def canteen_menu_feed_xml(menu, categories):
    xml = feed.render_menu(menu, categories)
    return _canteen_feed_xml(xml)


def canteen_meta_feed_xml(canteen):
    menu_feed_url = url_for('canteen_menu_feed',
                            canteen_name=canteen.key,
                            _external=True)
    xml = feed.render_meta(canteen, menu_feed_url)
    return _canteen_feed_xml(xml)


@app.route('/canteens/<canteen_name>')
@app.route('/canteens/<canteen_name>/meta')
def canteen_meta_feed(canteen_name):
    config = read_canteen_config()

    if canteen_name not in config:
        return canteen_not_found(config, canteen_name)

    canteen = config[canteen_name]
    return canteen_meta_feed_xml(canteen)


@app.route('/canteens/<canteen_name>/menu')
def canteen_menu_feed(canteen_name):
    config = read_canteen_config()

    if canteen_name not in config:
        return canteen_not_found(config, canteen_name)

    canteen = config[canteen_name]
    menu = get_menu(canteen)
    categories = get_meal_category(canteen)
    return canteen_menu_feed_xml(menu, categories)


@app.route('/')
@app.route('/canteens')
def canteen_index():
    config = read_canteen_config()
    return jsonify({
        key: url_for('canteen_meta_feed', canteen_name=key, _external=True)
        for key in config
    })


@app.route('/health_check')
def health_check():
    return make_response("OK", 200)
