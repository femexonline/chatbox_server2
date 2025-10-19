import mysql.connector
import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def env(name):
    return os.getenv(name)




def getApiPath(name):
    return env("HOST")+env("API_HOME")+name



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
        response = requests.post(getApiPath("send_msg_recv.php"), data=data)


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
        response = requests.post(getApiPath("msgs_recv_sig.php"), data=data)

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
        response = requests.post(getApiPath("msgs_seen_sig.php"), data=data)

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
        response = requests.post(getApiPath("new_chat_start.php"), data=data)

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
        response = requests.post(getApiPath("set_user_online.php"), data=data)

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
        response = requests.post(getApiPath("set_user_offline.php"), data=data)

        if response.ok:
            # res = response.text
            res = response.json()
            return res
        else:
            print("Request failed:", response.status_code, response.text)
            return None

