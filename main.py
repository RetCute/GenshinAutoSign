#Coded By Retrocal
import json
import requests
from urllib3 import disable_warnings
import datetime
import random
import uuid
import time
import utils.md5 as md5
import string
import utils.log as log


class AutoSign:
    def __init__(self):
        self.firsttime = True
        self.awardsurl = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home?act_id=e202009291139501'
        self.roleurl = 'https://api-takumi.mihoyo.com/binding/api/getUserGameRolesByCookie?game_biz=hk4e_cn'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.3.0',
            'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        self.signurl = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'
        self.SignInThread()

    def SignInThread(self):
        while True:
            if self.firsttime or (time.localtime().tm_hour == 4 and time.localtime().tm_min == 30 and time.localtime().tm_sec == 0):
                self.Init()
                self.firsttime = False

    def Init(self):
        self.conifg = self.getConfig()
        self.roles = []
        date = datetime.datetime.now()
        log.WriteLog(f"[INFO]今天是{date.year}.{date.month}.{date.day}")
        log.WriteLog(f"[INFO]导入了{len(self.conifg.cookies)}个Cookies")
        for cookies in self.conifg.cookies:
            roles = self.getRoles(cookies)
            if roles:
                self.roles.append(roles)
            else:
                log.WriteLog("[Error]失效Cookies" + json.dumps(cookies))
        log.WriteLog("[INFO]获取角色成功!")
        if len(self.roles) == 0:
            log.WriteLog("[Error]没有找到任何角色!")
            exit()
        self.infolist = []
        for i in self.roles:
            for role in i:
                url = f"https://api-takumi.mihoyo.com/event/bbs_sign_reward/info?region={role['region']}&act_id=e202009291139501&uid={role['game_uid']}"
                res = requests.get(url, headers=self.headers, verify=False, cookies=role["cookies"]).json()
                if res["retcode"] != 0:
                    log.WriteLog(f"[Error]获取签到信息失败.错误信息:{res['message']}")
                res['uid'] = role["game_uid"]
                res['cookies'] = role['cookies']
                res['region'] = role['region']
                self.infolist.append(res)
        self.SignIn(infolist=self.infolist)


    @staticmethod
    def get_ds():
        n = '9nQiU3AV0rJSIBWgdynfoGMGKaklfbM7'
        i = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        c = md5.md5('salt=' + n + '&t=' + i + '&r=' + r)
        return f'{i},{r},{c}'

    def SignIn(self, infolist):
        for info in infolist:
            total_sign_day = info['data']['total_sign_day']
            total_sign_day += 1
            awards = self.getawards(info["cookies"])
            awards = awards["data"]["awards"]
            log.WriteLog(f"[INFO]为UID:{info['uid']}签到中...")
            if info['data']['is_sign'] is True:
                log.WriteLog(F"[Waring]UID:{info['uid']}.您今日已经签到过了")
                pass
            elif info['data']['first_bind'] is True:
                log.WriteLog(F"[Warning]UID:{info['uid']}请先去米游社签到一次!")
                pass
            else:
                awardname = awards[total_sign_day]['name']
                cnt = awards[total_sign_day]['cnt']
                log.WriteLog(f"[INFO]UID:{info['uid']}今日的奖励是{cnt}{awardname}")
                headers = {
                    'DS': self.get_ds(),
                    'Origin': 'https://webstatic.mihoyo.com',
                    'x-rpc-app_version': "2.34.1",
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Version/4.0 Chrome/39.0.0.0 Mobile Safari/537.36 miHoYoBBS/2.3.0',
                    'x-rpc-client_type': "5",
                    'Referer': '',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,en-US;q=0.8',
                    'X-Requested-With': 'com.mihoyo.hyperion',
                    'x-rpc-device_id': str(uuid.uuid3(
                        uuid.NAMESPACE_URL, json.dumps(info["cookies"]))).replace('-', '').upper(),
                }
                data = {
                    'act_id': 'e202009291139501',
                    'region': info["region"],
                    'uid': info["uid"]
                }
                res = requests.post(self.signurl, json=data, headers=headers, cookies=info["cookies"], verify=False).json()
                if res["retcode"] != 0:
                    log.WriteLog(f"[Error]UID:{info['uid']}签到失败.错误信息:{res['message']}")
                else:
                    log.WriteLog(f"[INFO]UID:{info['uid']}签到成功!")

    def getawards(self, cookies):
        res = requests.get(self.awardsurl, headers=self.headers, cookies=cookies, verify=False).json()
        if res["retcode"] != 0:
            log.WriteLog("[Error]获取奖励失败!")
            return None
        return res

    def getRoles(self, cookies):
        res = requests.get(self.roleurl, cookies=cookies, headers=self.headers, verify=False).json()
        if res["retcode"] != 0:
            return False
        roles = res["data"]["list"]
        for role in roles:
            role["cookies"] = cookies
        return roles

    def getConfig(self):
        try:
            file = open("config.json", "r").read()
            config = json.loads(file)
            class Conifg:
                cookies = config["cookies"]
            return Conifg
        except FileNotFoundError:
            log.WriteLog("[Warning]未发现配置文件,重新生成中...")
            conifg = {"cookies": [{"ltoken": "", "cookie_token": "", "account_id": ""}]}
            open("config.json", "w").write(json.dumps(conifg, ensure_ascii=False))
            file = open("config.json", "r").read()
            config = json.loads(file)
            class Conifg:
                cookies = config["cookies"]
            return Conifg
        except json.JSONDecodeError:
            log.WriteLog("[Error]配置文件异常.请删除重试")
            exit()

disable_warnings()
AutoSign()
