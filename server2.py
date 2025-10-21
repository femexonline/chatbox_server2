import asyncio
import websockets
from websockets import WebSocketServerProtocol
import json
import time

from db_endpoints import EndPoints, env


admins={}
users={}

class Pings:
    # async def msgsDelivered(data, senderId, isAdmin, sockeetId):

    @staticmethod
    async def msgSent(resData, msgSendingID, senderId, isAdmin):
        send=[
            "msgsent",
            resData["msg"],
            msgSendingID,
            resData["isErr"],
            resData["err"],
        ]


        user_sockets={}
        if(isAdmin):
            user_sockets=admins
        else:
            user_sockets=users

        if(senderId in user_sockets):
            for socId in user_sockets[senderId]:
                webSoc:WebSocketServerProtocol=user_sockets[senderId][socId]
                if(not webSoc.closed):
                    await webSoc.send(json.dumps(send))
    
    @staticmethod
    async def notTheAdmin(chatID, senderId):
        send=[
            "nottheadmin",
            chatID,
        ]

        if(senderId in admins):
            for socId in admins[senderId]:
                webSoc:WebSocketServerProtocol=admins[senderId][socId]
                if(not webSoc.closed):
                    await webSoc.send(json.dumps(send))

    @staticmethod
    async def notTheAdmins(chatID, senderId):
        send=[
            "nottheadmins",
            chatID,
        ]

        for adminId in admins:
            if(senderId!=adminId):
                for socId in admins[adminId]:
                    webSoc:WebSocketServerProtocol=admins[adminId][socId]
                    if(not webSoc.closed):
                        await webSoc.send(json.dumps(send))


    @staticmethod
    async def newMsg(chatData, resData, senderId, isAdmin):
        if(resData["isErr"]):
            return
                
        newAdmin=None
        if(isAdmin):
            if(not chatData["admin_id"]):
                newAdmin=senderId
                None
        
        send=[
            "newmsg",
            resData["msg"],
            newAdmin
        ]

        # send to all admin if no admin
        if(not isAdmin):
            if(not chatData["admin_id"]):

                for adminId in admins:
                    for socId in admins[adminId]:
                        webSoc:WebSocketServerProtocol=admins[adminId][socId]
                        if(not webSoc.closed):
                            await webSoc.send(json.dumps(send))
            
                return



        user_sockets={}
        recieverId=0
        if(isAdmin):
            user_sockets=users
            recieverId=chatData["user_id"]
        else:
            user_sockets=admins
            recieverId=chatData["admin_id"]

        recieverId=str(recieverId)

        # print(user_sockets[int(recieverId)])
        if(recieverId in user_sockets):
            for socId in user_sockets[recieverId]:
                webSoc:WebSocketServerProtocol=user_sockets[recieverId][socId]
                if(not webSoc.closed):
                    await webSoc.send(json.dumps(send))

        if(isAdmin):
            if(newAdmin):
                await Pings.notTheAdmins(chatData["id"], senderId)

    @staticmethod
    async def onlineStatus(status, userId, recipients:list, senderIsAdmin:bool):
        send=[
            "onlinestatus",
            status,
            userId,
        ]

        user_sockets={}
        if(senderIsAdmin):
            user_sockets=users
        else:
            user_sockets=admins


        for recipientId in recipients:
            recipientId=str(recipientId)

            if(recipientId in user_sockets):
                for socId in user_sockets[recipientId]:
                    webSoc:WebSocketServerProtocol=user_sockets[recipientId][socId]
                    if(not webSoc.closed):
                        await webSoc.send(json.dumps(send))

    @staticmethod
    async def msgsDelivered(chatId, msgIds_str,  idToRecieve, idIsAdmin, time_del):
        send=[
            "msgsdelivered",
            chatId,
            msgIds_str,
            time_del
        ]

        user_sockets={}
        if(idIsAdmin):
            user_sockets=admins
        else:
            user_sockets=users

        idToRecieve=str(idToRecieve)
        if(idToRecieve in user_sockets):

            for socId in user_sockets[idToRecieve]:
                webSoc:WebSocketServerProtocol=user_sockets[idToRecieve][socId]
                if(not webSoc.closed):
                    await webSoc.send(json.dumps(send))
    
    @staticmethod
    async def msgsSeen(chatId, msgIds_str,  idToRecieve, idIsAdmin, time_del):
        send=[
            "msgsseen",
            chatId,
            msgIds_str,
            time_del
        ]

        user_sockets={}
        if(idIsAdmin):
            user_sockets=admins
        else:
            user_sockets=users

        idToRecieve=str(idToRecieve)
        if(idToRecieve in user_sockets):

            for socId in user_sockets[idToRecieve]:
                webSoc:WebSocketServerProtocol=user_sockets[idToRecieve][socId]
                if(not webSoc.closed):
                    await webSoc.send(json.dumps(send))
    



class SocketMsgRecieve:
    @staticmethod
    async def recieve(message, userid, isAdmin, sockeetId):


        message=json.loads(message)
        msg_type=message[0]

        if(msg_type=="sendmsg"):
            await SocketMsgRecieve._sendmsg(message, userid, isAdmin, sockeetId)

        if(msg_type=="msgrecvsig"):
            await SocketMsgRecieve._msgsRecvSig(message, userid, isAdmin)

        if(msg_type=="msgseensig"):
            await SocketMsgRecieve._msgSeenSig(message, userid, isAdmin)

        if(msg_type=="newchatstart"):
            await SocketMsgRecieve._newChatStart(message, userid, isAdmin)

    @staticmethod
    async def _sendmsg(message:list, senderId, isAdmin, sockeetId):
        chatID=message[1]
        msgSendingID=message[2]
        msg=message[3]
        resId=message[4]
        seen=message[5]


        #chatID, senderId, msg, resId
        #adminFirstRes, pingNotTheAdmin, chatData, (isErr, msg, err)resData
        apiData=EndPoints.sendmsg_recv(chatID, senderId, msg, isAdmin, resId)
        if(apiData["isErr"]):
            print(apiData["err"])
            print("err_1")
            return

        
        if(apiData["pingNotTheAdmin"]):
            await Pings.notTheAdmin(chatID, senderId)
            return


        
        await Pings.msgSent(apiData, msgSendingID, senderId, isAdmin)
        await Pings.newMsg(apiData["chatData"], apiData, senderId, isAdmin)

        if(apiData["adminFirstRes"]):
            if(seen):
                msgTemp_={}
                msgTemp_[chatID]=seen
                msgTemp=[
                    "msgrecvsig",
                    msgTemp_
                ]
                await SocketMsgRecieve._msgsRecvSig(msgTemp, senderId, isAdmin)
                await SocketMsgRecieve._msgSeenSig(msgTemp, senderId, isAdmin)
        

    @staticmethod
    async def _msgsRecvSig(message:list, senderId, isAdmin):
        data=message[1]
        if(not len(data)):
           return
        

        time_del=int(time.time())
        toSend=json.dumps(data)


        resData=EndPoints.msgsRecvSig(toSend, time_del, senderId, isAdmin)
        if(resData["isErr"]):
            print(resData["err"])
            print("err_2")
            return
                

        for r_data in resData["data"]:
            chatId=str(r_data["chat_id"])

            if(chatId in data):
                idToRecieve=r_data["idToRecieve"]
                await Pings.msgsDelivered(chatId, data[chatId], idToRecieve, not isAdmin, time_del)

    @staticmethod
    async def _msgSeenSig(message:list, senderId, isAdmin):
        data=message[1]
        if(not len(data)):
           return
        

        time_del=int(time.time())
        toSend=json.dumps(data)


        resData=EndPoints.msgSeenSig(toSend, time_del, senderId, isAdmin)
        if(resData["isErr"]):
            print(resData["err"])
            print("err_3")
            return
        

        for r_data in resData["data"]:
            chatId=str(r_data["chat_id"])

            if(chatId in data):
                idToRecieve=r_data["idToRecieve"]
                await Pings.msgsSeen(chatId, data[chatId], idToRecieve, not isAdmin, time_del)


    @staticmethod
    async def _newChatStart(message:list, senderId, isAdmin):
        msg_id=message[1]        
        
        if(not msg_id):
           return
        
        
        resData=EndPoints.newChatStart(msg_id)
        if(resData["isErr"]):
            print(resData["err"])
            print("err_4")
            return


        resDatar={
            "isErr":False,
            "err":"",
            "msg":resData["msg"]
        }

        await Pings.newMsg(resData["chatData"], resDatar, senderId, isAdmin)

        






async def processUserEnter(userid, isAdmin, sockeetId, websocket):
    setOnline=False

    if(not isAdmin):
        if(userid not in users):
            setOnline=True
            users[userid]={}

        if(sockeetId not in users[userid]):
            users[userid][sockeetId]=websocket

    else:
        if(userid not in admins):
            setOnline=True
            admins[userid]={}

        if(sockeetId not in admins[userid]):
            admins[userid][sockeetId]=websocket

    if(setOnline):
        resData=EndPoints.setUserOnline(userid, isAdmin)
        if(resData["isErr"]):
            print(resData["err"])
            print("err_5")
            return

        await Pings.onlineStatus(resData["user_status"], userid, resData["list_to_notify"], isAdmin)

        
async def processUserLeave(userid, isAdmin, sockeetId):
    setOffline=False

    if(not isAdmin):
        if(userid in users):
            if(sockeetId in users[userid]):
                users[userid].pop(sockeetId)
            
            if(not len(users[userid])):
                users.pop(userid)
                setOffline=True
        else:
            print("some err")

    else:
        if(userid in admins):
            if(sockeetId in admins[userid]):
                admins[userid].pop(sockeetId)
            
            if(not len(admins[userid])):
                admins.pop(userid)
                setOffline=True
        else:
            print("some err2")

    if(setOffline):
        resData=EndPoints.setUserOffline(userid, isAdmin)
        if(resData["isErr"]):
            print(resData["err"])
            print("err_6")
            return

        await Pings.onlineStatus(resData["user_status"], userid, resData["list_to_notify"], isAdmin)


async def handle_connection(websocket:WebSocketServerProtocol, path):
    print("A client connected!")

    data=path.split("/")
    userid=data[1]
    isAdmin=int(data[2])
    sockeetId=data[3]
    
    await processUserEnter(userid, isAdmin, sockeetId, websocket)


    try:
        while True:
            # Set a timeout for receiving messages
            message = await asyncio.wait_for(websocket.recv(), timeout=30)  # 10 seconds timeout
            if(message):
                print(sockeetId)
                await SocketMsgRecieve.recieve(message, userid, isAdmin, sockeetId)
    except asyncio.TimeoutError:
        print("Client timed out - no messages received for 10 seconds")
        await processUserLeave(userid, isAdmin, sockeetId)
    except websockets.ConnectionClosed:
        print("A client disconnected")
        await processUserLeave(userid, isAdmin, sockeetId)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        await processUserLeave(userid, isAdmin, sockeetId)

async def main():
    async with websockets.serve(handle_connection, env("HOST"), int(env("PORT"))):
        print("WebSocket server is running on ws://{}:{}".format(env("HOST"), env("PORT")))
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
