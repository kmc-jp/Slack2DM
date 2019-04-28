# coding: utf-8

import os
import time
import websocket
from requests_oauthlib import OAuth1Session
import random
import json
from slackclient import SlackClient
import re

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)

pat_send = re.compile(r"^(sendDM|senddm) `(.*?)` (.*)$")

CK = os.environ["CK"]
CS = os.environ["CS"]
AT = os.environ["AT"]
AS = os.environ["AS"]

# ツイート投稿用のURL
DMurl = "https://api.twitter.com/1.1/direct_messages/events/new.json"

# OAuth認証で POST method で投稿
twitter = OAuth1Session(CK, CS, AT, AS)


def get_uid(screen_name):
    url = "https://api.twitter.com/1.1/users/show.json?screen_name=" + screen_name
    ret_json = twitter.get(url)
    if ret_json.status_code == 200:
        return (json.loads(ret_json.text))["id"]
    else:
        print("Error: %d" % ret_json.status_code)
        return 0 # 多分uid 0 はいないでしょ


def post_DM(id, text):
    params = {'event': {'type': 'message_create', 'message_create': {'target': {'recipient_id': id},'message_data': {'text': text}}}}
    req = twitter.post(DMurl, data=json.dumps(params))
    if req.status_code == 200:
        return req.status_code
    else:
        print("Error: %d" % req.status_code)
        return req.status_code


def post_msg(msg, channel, unfurl=True):
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=msg,
        icon_emoji=":mawarunos:",
        unfurl_links=unfurl,
        username="DM送るやつ"
    )


def main_process(rtm):
    r = pat_send.match(rtm["text"])
    if r:
        res_status = post_DM(get_uid(r.group(2)), r.group(3))
        if res_status == 200:
            post_msg("Success", rtm["channel"])
        else:
            post_msg("Failed: " + res_status, rtm["channel"])


if __name__ == "__main__":
    if sc.rtm_connect():
        while True:
            try:
                for rtm in sc.rtm_read():
                    if rtm["type"] == "message" and rtm["channel"] == "C0A6X3D7E": # n C61K9HKDM, m "C0A6X3D7E" n2 C9D1NBX9B
                        if "subtype" not in rtm and "text" in rtm: # ここキレイになんないかな………
                            main_process(rtm)
            except:
                time.sleep(2)
                if sc.rtm_connect():
                    pass
                else:
                    print("Connection Failed!")
                    time.sleep(100)
            time.sleep(0.5)
    else:
        print("Connection Failed")
