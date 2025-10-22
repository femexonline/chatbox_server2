import time
import os
import requests
from dotenv import load_dotenv


load_dotenv()
if(os.getenv("LIVE")=="false"):
    load_dotenv(".env.dev", override=True)


def env(name):
    return os.getenv(name)



def getApiPath(name):
    return env("API_HOST")+env("API_HOME")+name


VerifySsl=True
if(os.getenv("VERIFY_SSL")=="false"):
    VerifySsl=False

    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EndPoints:

    @staticmethod
    def sendmsg_recv(chatID, senderId, msg, isAdmin, resId=None):
        data = {
            "chatID": chatID,
            "senderId": senderId,
            "msg": msg,
            "isAdmin": isAdmin,
            "resId": resId,
        }


        # send POST request
        response = requests.post(
            getApiPath("send_msg_recv.php"), 
            data=data,
            verify=VerifySsl
        )


        if response.ok:
            # res = response.text
            res = response.json()

            return res
        else:
            print("Request failed:", response.status_code, response.text)
            return None

    @staticmethod
    def msgsRecvSig(chatDataJson, time, senderId, isAdmin):
        data = {
            "chatsData": chatDataJson,
            "time": time,
            "senderId": senderId,
            "isAdmin": isAdmin,
        }

        # send POST request
        response = requests.post(
            getApiPath("msgs_recv_sig.php"), 
            data=data,
            verify=VerifySsl
        )

        if response.ok:
            # res = response.text
            res = response.json()
            return res
        else:
            print("Request failed:", response.status_code, response.text)
            return None

    @staticmethod
    def msgSeenSig(chatDataJson, time, senderId, isAdmin):
        data = {
            "chatsData": chatDataJson,
            "time": time,
            "senderId": senderId,
            "isAdmin": isAdmin,
        }

        # send POST request
        response = requests.post(
            getApiPath("msgs_seen_sig.php"), 
            data=data,
            verify=VerifySsl
        )

        if response.ok:
            # res = response.text
            res = response.json()
            return res
        else:
            print("Request failed:", response.status_code, response.text)
            return None

    @staticmethod
    def newChatStart(msg_id):
        data = {
            "msg_id": msg_id,
        }

        # send POST request
        response = requests.post(
            getApiPath("new_chat_start.php"), 
            data=data,
            verify=VerifySsl
        )

        if response.ok:
            # res = response.text
            res = response.json()
            return res
        else:
            print("Request failed:", response.status_code, response.text)
            return None

    @staticmethod
    def setUserOnline(user_id, isAdmin):
        data = {
            "user_id": user_id,
            "isAdmin": isAdmin,
        }

        # send POST request
        response = requests.post(
            getApiPath("set_user_online.php"), 
            data=data,
            verify=VerifySsl
        )

        if response.ok:
            # res = response.text
            res = response.json()
            return res
        else:
            print("Request failed:", response.status_code, response.text)
            return None

    @staticmethod
    def setUserOffline(user_id, isAdmin):
        data = {
            "user_id": user_id,
            "isAdmin": isAdmin,
            "time": int(time.time()),
        }

        # send POST request
        response = requests.post(
            getApiPath("set_user_offline.php"), 
            data=data,
            verify=VerifySsl
        )

        if response.ok:
            # res = response.text
            res = response.json()
            return res
        else:
            print("Request failed:", response.status_code, response.text)
            return None

