import base64
import re
from io import BytesIO

import ujson as json

from core.builtins import Bot
from core.builtins.message import Image, Url
from core.component import module
from core.dirty_check import check_bool, rickroll
from core.utils.http import download, get_url
from core.utils.text import isint
from core.utils.web_render import webrender
from PIL import Image as PILImage


t = module('tweet',
           developers=['Dianliang233'],
           desc='{tweet.help.desc}', doc=True,
           alias=['x']
           )


@t.handle('<tweet> {{tweet.help}}')
async def _(msg: Bot.MessageSession, tweet: str):
    if isint(tweet):
        tweet_id = tweet
    else:
        match = re.search(r"status/(\d+)", tweet)
        if match:
            tweet_id = match.group(1)
        else:
            await msg.finish(msg.locale.t('tweet.message.invalid'))

    web_render = webrender('element_screenshot')
    if not web_render:
        await msg.finish(msg.locale.t("error.config.webrender.invalid"))

    try:
        res = await get_url(f'https://react-tweet.vercel.app/api/tweet/{tweet_id}', 200)
    except ValueError as e:
        if str(e).startswith('404'):
            await msg.finish(msg.locale.t('tweet.message.invalid'))
        else:
            raise e

    res_json = json.loads(res)
    if not res_json['data']:
        await msg.finish(msg.locale.t('tweet.message.not_found'))
    elif res_json['data']['__typename'] == "TweetTombstone":
        await msg.finish(f"{msg.locale.t('tweet.message.tombstone')}{res_json['data']['tombstone']['text']['text'].replace(' Learn more', '')}")
    else:
        if await check_bool(res_json['data']['text'], res_json['data']['user']['name'],
                            res_json['data']['user']['screen_name']):
            await msg.finish(rickroll(msg))

        css = '''
            main {
                justify-content: start !important;
            }

            main > div {
                margin: 0 !important;
                border: 0 !important;
            }

            article {
                padding: .75rem 1rem;
            }

            footer {
                display: none;
            }

            #__next > div {
                height: auto;
                padding: 0;
            }

            a[href^="https://twitter.com/intent/follow"],
            a[href^="https://help.twitter.com/en/twitter-for-websites-ads-info-and-privacy"],
            div[class^="tweet-replies"],
            button[aria-label="Copy link"],
            a[aria-label="Reply to this Tweet on Twitter"],
            span[class^="tweet-header_separator"] {
                display: none;
            }
        '''

        pic = await download(web_render, method='POST', headers={
            'Content-Type': 'application/json',
        }, post_data=json.dumps(
            {'url': f'https://react-tweet-next.vercel.app/light/{tweet_id}', 'css': css, 'mw': False,
             'element': 'article'}), request_private_ip=True)
        read = open(pic)
        load_img = json.loads(read.read())
        img_lst = []
        for x in load_img:
            b = base64.b64decode(x)
            bio = BytesIO(b)
            bimg = PILImage.open(bio)
            img_lst.append(Image(bimg))
        img_lst.append(Url(f"https://twitter.com/{res_json['data']['user']['screen_name']}/status/{tweet_id}"))
        await msg.finish(img_lst)
