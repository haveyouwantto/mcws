# -*- coding:utf-8 -*-

import datetime
import json

import requests

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from static import ref_strings


def getUserData(username, language='en-us'):
    auth = open("../files/login.txt").read()

    # 请求头设置
    payloadHeader = {
        "Host": "account.xbox.com",
        "Content-Length": "667",
        "Origin": "https: //account.xbox.com",
        "onerf-spa": "1",
        "content-type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
        "__RequestVerificationToken": "bd3bCXMIhO3VLHDRc7lP3THkc1D-lZW__aRIKwFOBAOGR\
_hTdeNHuXKbtBt-SDMmUpma6WZM2xWWBrmeQFZD_hOkt-GUnQqlf4YkaNsTh-dB31D30",
        "Cookie": "RPSSecAuth=" + auth + "; __RequestVerificationToken=GRc-HbSOI8Hz8\
XyfQe3aLFeP2K9rWFe5rRf2ctLrAaRIRrY2oLpTZ25S1Z6LX2vimOjFSzfjnG9c5N0kfKXiDPVKlxY1;"
    }

    postUrl = 'https://account.xbox.com/' + language + \
              '/profile?gamertag=' + username.replace(" ", "%20")
    timeOut = 25

    res = requests.get(postUrl, headers=payloadHeader,
                       timeout=timeOut, allow_redirects=True)

    if res.status_code != 200:
        print(
            f"responseTime = {datetime.datetime.now()}, statusCode = {res.status_code}")

    if res.status_code > 299:
        raise ConnectionError('API changed')

    rejson = json.loads(res.text)
    HttpStatusCode = rejson['HttpStatusCode']
    if HttpStatusCode == 302:
        login(rejson)
        return getUserData(username, language)

    try:
        xboxData = rejson['PrimaryArea']['Regions'][0]['Modules'][0]['DetailViewModel']
        return xboxData
    except:
        print(rejson)


def login(rejson):
    print(ref_strings.xboxapi.login)
    url = rejson["RedirectUrl"]
    driver = webdriver.Chrome()
    driver.get(url)

    WebDriverWait(driver, 60, 1).until(
        lambda driver: driver.find_element_by_id('uhfCatLogo')
    )

    cookies = driver.get_cookies()
    for i in cookies:
        if i["name"] == "RPSSecAuth":
            key = i["value"]
            print(key)
            f = open("../files/login.txt", "w")
            f.write(key)
            f.close()

            driver.quit()
