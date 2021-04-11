# -*- coding:utf-8 -*-

# Part of https://github.com/bakashigure/aqua_bot
# Modified from https://saucenao.com/tools/examples/api/identify_images_v1.1.py
# Created by bakashigure
# Last updated 2021/4/3


import asyncio
import codecs
import io
import json
import os
import re
import sys
import time
import unicodedata
from collections import OrderedDict

import pixivpy3
import requests
from PIL import Image

from .secret import APIKEY


class Saucenao:
    def __init__(self):

        self.api_key = APIKEY
        self.minsim = '80!'

        self.thumbSize = (250, 250)

        # enable or disable indexes
        self.index_hmags = '0'
        self.index_reserved = '0'
        self.index_hcg = '0'
        self.index_ddbobjects = '0'
        self.index_ddbsamples = '0'
        self.index_pixiv = '1'
        self.index_pixivhistorical = '1'
        self.index_reserved = '0'
        self.index_seigaillust = '1'
        self.index_danbooru = '0'
        self.index_drawr = '1'
        self.index_nijie = '1'
        self.index_yandere = '0'
        self.index_animeop = '0'
        self.index_reserved = '0'
        self.index_shutterstock = '0'
        self.index_fakku = '0'
        self.index_hmisc = '0'
        self.index_2dmarket = '0'
        self.index_medibang = '0'
        self.index_anime = '0'
        self.index_hanime = '0'
        self.index_movies = '0'
        self.index_shows = '0'
        self.index_gelbooru = '0'
        self.index_konachan = '0'
        self.index_sankaku = '0'
        self.index_animepictures = '0'
        self.index_e621 = '0'
        self.index_idolcomplex = '0'
        self.index_bcyillust = '0'
        self.index_bcycosplay = '0'
        self.index_portalgraphics = '0'
        self.index_da = '1'
        self.index_pawoo = '0'
        self.index_madokami = '0'
        self.index_mangadex = '0'

        self.db_bitmask = int(self.index_mangadex+self.index_madokami+self.index_pawoo+self.index_da+self.index_portalgraphics+self.index_bcycosplay+self.index_bcyillust+self.index_idolcomplex+self.index_e621+self.index_animepictures+self.index_sankaku+self.index_konachan+self.index_gelbooru+self.index_shows+self.index_movies+self.index_hanime+self.index_anime+self.index_medibang +
                              self.index_2dmarket+self.index_hmisc+self.index_fakku+self.index_shutterstock+self.index_reserved+self.index_animeop+self.index_yandere+self.index_nijie+self.index_drawr+self.index_danbooru+self.index_seigaillust+self.index_anime+self.index_pixivhistorical+self.index_pixiv+self.index_ddbsamples+self.index_ddbobjects+self.index_hcg+self.index_hanime+self.index_hmags, 2)
        print("dbmask="+str(self.db_bitmask))

    async def saucenao_search(self, file_path: str):
        _msg = {}

        image = Image.open(file_path)
        image = image.convert('RGB')
        image.thumbnail(self.thumbSize, resample=Image.ANTIALIAS)
        imageData = io.BytesIO()
        image.save(imageData, format='PNG')

        url = 'http://saucenao.com/search.php?output_type=2&numres=1&minsim=' + \
            self.minsim+'&dbmask=' + \
            str(self.db_bitmask)+'&api_key='+self.api_key
        files = {'file': (file_path, imageData.getvalue())}
        imageData.close()

        processResults = True
        while True:
            r = requests.post(url, files=files)
            if r.status_code != 200:
                if r.status_code == 403:
                    return json.dumps([
                        {'type': "error", 'message': "Incorrect or Invalid API Key! Please Edit Script to Configure..."}
                    ])

                else:
                    # generally non 200 statuses are due to either overloaded servers or the user is out of searches
                    return json.dumps([
                        {'type': "error", 'message': "status code: " +
                            str(r.status_code)}
                    ])
            else:
                results = json.JSONDecoder(
                    object_pairs_hook=OrderedDict).decode(r.text)
                if int(results['header']['user_id']) > 0:
                    # api responded
                    print('Remaining Searches 30s|24h: '+str(
                        results['header']['short_remaining'])+'|'+str(results['header']['long_remaining']))
                    if int(results['header']['status']) == 0:
                        # search succeeded for all indexes, results usable
                        break
                    else:
                        if int(results['header']['status']) > 0:
                            # One or more indexes are having an issue.
                            # This search is considered partially successful, even if all indexes failed, so is still counted against your limit.
                            # The error may be transient, but because we don't want to waste searches, allow time for recovery.
                            return json.dumps([
                                {'type': "error", 'message': "API Error. "}
                            ])
                            # time.sleep(600)
                        else:
                            # Problem with search as submitted, bad image, or impossible request.
                            # Issue is unclear, so don't flood requests.
                            return json.dumps([
                                {'type': "error",
                                    'message': "Bad image or other request error. "}
                            ])
                else:
                    # General issue, api did not respond. Normal site took over for this error state.
                    # Issue is unclear, so don't flood requests.
                    return json.dumps([
                        {'type': "error", 'message': "Bad image, or API failure. "}
                    ])

        if processResults:
            # print(results)

            if int(results['header']['results_returned']) > 0:
                artwork_url = ""
                # one or more results were returned
                if float(results['results'][0]['header']['similarity']) > float(results['header']['minimum_similarity']):
                    print('hit! '+str(results['results']
                                      [0]['header']['similarity']))

                    # get vars to use
                    service_name = ''
                    illust_id = 0
                    member_id = -1
                    index_id = results['results'][0]['header']['index_id']
                    page_string = ''
                    page_match = re.search(
                        '(_p[\d]+)\.', results['results'][0]['header']['thumbnail'])
                    if page_match:
                        page_string = page_match.group(1)

                    if index_id == 5 or index_id == 6:
                        # 5->pixiv 6->pixiv historical
                        service_name = 'pixiv'
                        member_id = results['results'][0]['data']['member_id']
                        illust_id = results['results'][0]['data']['pixiv_id']
                        artwork_url = "https://pixiv.net/artworks/{}".format(
                            illust_id)
                        _msg = {
                            "type": "text",
                            "data": {
                                "text": "找到了! {0}%\nsource: {1}".format(str(results['results'][0]['header']['similarity']), artwork_url)
                            }
                        }
                        return _msg
                    elif index_id == 8:
                        # 8->nico nico seiga
                        service_name = 'seiga'
                        member_id = results['results'][0]['data']['member_id']
                        illust_id = results['results'][0]['data']['seiga_id']
                    elif index_id == 10:
                        # 10->drawr
                        service_name = 'drawr'
                        member_id = results['results'][0]['data']['member_id']
                        illust_id = results['results'][0]['data']['drawr_id']
                    elif index_id == 11:
                        # 11->nijie
                        service_name = 'nijie'
                        member_id = results['results'][0]['data']['member_id']
                        illust_id = results['results'][0]['data']['nijie_id']
                    elif index_id == 34:
                        # 34->da
                        service_name = 'da'
                        illust_id = results['results'][0]['data']['da_id']
                    else:
                        # unknown
                        print('Unhandled Index! Exiting...')
                        sys.exit(2)

                else:
                    return json.dumps([
                        {'type': "error", 'message': "没找到. {0}% \n请提高最低匹配阈值或换张图".format(str(results['results'][0]['header']['similarity']))}
                    ])


            else:
                return json.dumps([
                    {'type': "error", 'message': "no results...  ;_;"}
                ])

            if int(results['header']['long_remaining']) < 1:  # could potentially be negative
                return json.dumps([
                    {'type': "error", 'message': "Out of searches today. "}
                ])

            if int(results['header']['short_remaining']) < 1:
                return json.dumps([
                    {'type': "error", 'message': "Out of searches in 30s. "}
                ])
