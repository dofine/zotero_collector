import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, jsonify, request
import json
from dateutil.parser import parse as parse_date
from cachetools import LRUCache
from pyzotero import zotero
from dataclasses import dataclass
import re

zotero_config = json.loads(open("config.json").read().strip())
zot = zotero.Zotero(zotero_config["zotero_user"], "user",
                    zotero_config["zotero_key"])

app = Flask(__name__)


def parse_xyz_fm(podcast_url):
    podcast_content = requests.get(podcast_url).content
    soup = BeautifulSoup(podcast_content, "lxml")
    try:
        show_title = soup.find("meta", {"property": "og:title"})["content"]
        show_audio = soup.find("meta", {"property": "og:audio"})["content"]
        j = json.loads(
            soup.find("script", {
                "type": "application/ld+json",
                "name": "schema:podcast-show"
            }).text)
        date_published = datetime.strftime(parse_date(j["datePublished"]),
                                           "%Y-%m-%d")
        series = j["partOfSeries"]["name"]
        series_homepage = j["partOfSeries"]["url"]
        d = {
            "title": show_title,
            "audio": show_audio,
            "date": date_published,
            "series": series,
            "homepage": series_homepage,
            "url": j["url"],
            "desc": j["description"],
            "runningTime":
            j["timeRequired"].split("PT")[1].split("M")[0] + "min",
        }
        return d
    except:
        return None


def parse_weixin(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'lxml')
    d = {}
    d['author'] = soup.find('meta', {'name': 'author'})['content']  # 作者的名字
    d['title'] = soup.find('meta', {'property': 'og:title'})['content']
    d['desc'] = soup.find('meta', {'name': 'description'})['content']
    d['site_name'] = soup.find('meta', {'property': 'og:site_name'})['content']
    d['weixin_name'] = soup.find('a', {'id': 'js_name'}).text.strip()  # 公众号的名称
    p_re = re.compile(
        '0,\"(\d+)\",0,document.getElementById\(\"publish_time\"\)')
    m = p_re.search(page.text)
    if m:
        d['publish_time'] = datetime.fromtimestamp(int(
            m.group(1))).strftime('%Y-%m-%d')
    return d


@app.route("/zotero/<string:platform>", methods=["POST"])
def resp(platform):
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        return {"status": -1, "data": {"message": "content-type must be json"}}
    data = request.get_json()
    url = data["url"]
    app.logger.info('get request of %s', url)
    if platform == 'xyz':
        d = parse_xyz_fm(url)
        if d is not None:
            podcast_info = d
            podcast = zot.item_template(itemtype="podcast")
            podcast["title"] = podcast_info["title"]
            podcast["abstractNote"] = podcast_info["desc"]
            podcast["seriesTitle"] = podcast_info["series"]
            podcast["url"] = podcast_info["url"]
            podcast["language"] = "zh-CN"
            podcast["collections"] = [zotero_config["zotero_collection"]]
            podcast["runningTime"] = podcast_info["runningTime"]
            podcast['creators'][0]['firstName'] = podcast_info["series"]  # 暂时这样凑合着
            zot_resp = zot.create_items([podcast])
    elif platform == 'weixin':
        d = parse_weixin(url)
        app.logger.info(d)
        webpage = zot.item_template('webpage')
        webpage['title'] = d['title']
        webpage['abstractNote'] = d['desc']
        webpage['url'] = url
        webpage['collections'] = [zotero_config["zotero_collection"]]
        webpage['websiteTitle'] = d['weixin_name']
        webpage['websiteType'] = '微信公众平台'
        webpage['creators'][0]['firstName'] = d['author']
        webpage['date'] = d['publish_time']
        zot_resp = zot.create_items([webpage])

    if len(zot_resp["success"]) > 0:
        return {"status": 0, "data": {"key": zot_resp["success"]["0"]}}
    else:
        return {"status": 1, "data": zot_resp["failed"]}


if __name__ == "__main__":
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5678, host="0.0.0.0")
