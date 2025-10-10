import mysql.connector
import time
import os
from dotenv import load_dotenv

load_dotenv()

def env(name):
    return os.getenv(name)






mydb = mysql.connector.connect(
    host=env("HOST"),
    user=env("DB_UNAME"),
    password=env("DB_PASS"),
    database=env("DB_NAME"),
)





def _convertListToSqlList(lisstData:list):
    # // Join the array elements with commas
    
    res="("
    index=0
    for data in lisstData:
        if(index):
            res+=","
        res+=str(data)

        index+=1

    res+=")"
    return res



class MessageConnector:

    @staticmethod
    def _getMsgById(id, reconnect=False):
        if(reconnect):
            mydb.reconnect()

        mycursor = mydb.cursor(dictionary=True)

        mycursor.execute("SELECT * FROM messages WHERE id='"+str(id)+"'")

        myresult = mycursor.fetchone()

        return myresult

    @staticmethod
    def _addMessage(chatID, userID, msg):
        mycursor = mydb.cursor()

        read_status="sent"
        time_sent=int(time.time())

        sql="""INSERT INTO messages (chat_id, sender_id, msg, time_sent, read_status) VALUES 
            (%s, %s, %s, %s, %s)
        """
        val = (chatID, userID, msg, time_sent, read_status)
        mycursor.execute(sql, val)

        mydb.commit()

        return mycursor.lastrowid

        print(mycursor.rowcount, "record inserted.")

    @staticmethod
    def sendDirectMsg(userID, chatID, msg, resId):

        res={
            "isErr":False,
            "msg":[],
            "err":"",
        }

        msgId=MessageConnector._addMessage(chatID, userID, msg)
        if(not msgId):
            res["isErr"]=True
            res["err"]="Some error occured"

        if(not res["isErr"]):
            msg=MessageConnector._getMsgById(msgId)

            if(not msg):
                res["isErr"]=True
                res["err"]="Some error occured"
                

        if(not res["isErr"]):
            res["msg"]=msg


        return res

    @staticmethod
    def markMessagesFromChatAsDelivered(chatID:int, msgIds_str, userID:int, time_del):
        
        if(len(msgIds_str) < 2):
            return
        
        msgIds_str=msgIds_str.split("_")
        lastId=msgIds_str[0]
        firstId=msgIds_str[1]

        mycursor = mydb.cursor()
        

        sql = "UPDATE messages SET read_status = 'delivered', deliver_time = '"+str(time_del)+"' "
        # sql = "UPDATE messages SET read_status = 'sent', deliver_time = '"+str(time_del)+"' "
        
        if(firstId):
            sql+="WHERE id >= '"+firstId+"' AND id <= '"+lastId+"' "
        else:
            sql+="WHERE id = '"+lastId+"' "

        sql+="AND sender_id != '"+str(userID)+"' AND read_status='sent'"
        sql+="AND chat_id = '"+str(chatID)+"'"
        mycursor.execute(sql)

        mydb.commit()

    @staticmethod
    def markMessagesFromChatAsSeen(chatID:int, msgIds_str, userID:int, time_del):
        
        if(len(msgIds_str) < 2):
            return
        
        msgIds_str=msgIds_str.split("_")
        lastId=msgIds_str[0]
        firstId=msgIds_str[1]

        mycursor = mydb.cursor()
        

        sql = "UPDATE messages SET read_status = 'read', read_time = '"+str(time_del)+"' "
        # sql = "UPDATE messages SET read_status = 'delivered', read_time = '"+str(time_del)+"' "
        
        if(firstId):
            sql+="WHERE id >= '"+firstId+"' AND id <= '"+lastId+"' "
        else:
            sql+="WHERE id = '"+lastId+"' "

        sql+="AND sender_id != '"+str(userID)+"' "
        sql+="AND chat_id = '"+str(chatID)+"' AND read_status='delivered'"
        mycursor.execute(sql)

        mydb.commit()




class ChatConnector:
    @staticmethod
    def getChatByid(id):
        mycursor = mydb.cursor(dictionary=True)

        mycursor.execute("SELECT * FROM chats WHERE id='"+str(id)+"'")

        myresult = mycursor.fetchone()

        return myresult

    @staticmethod
    def setChatAdmin(id, admin_id):
        mycursor = mydb.cursor()

        sql = "UPDATE chats SET admin_id = '"+str(admin_id)+"' WHERE id = '"+str(id)+"'"

        mycursor.execute(sql)

        mydb.commit()

    @staticmethod
    def getUserIdsConnectedAdminAndOnline(adminId):
        mycursor = mydb.cursor(dictionary=True)

        sql="SELECT c.user_id FROM chats AS c "
        sql+="LEFT JOIN users AS u ON c.user_id=u.id "
        sql+="WHERE u.last_seen='online' AND c.admin_id='"+str(adminId)+"'"

        mycursor.execute(sql)

        myresult = mycursor.fetchall()
        data=[]
        for d in myresult:
            data.append(d["user_id"])

        return data

    @staticmethod
    def getAdminIdsConnectedUserAndOnline(userId):
        mycursor = mydb.cursor(dictionary=True)

        sql="SELECT c.admin_id FROM chats AS c "
        sql+="LEFT JOIN users AS u ON c.admin_id=u.id "
        sql+="WHERE u.last_seen='online' AND c.user_id='"+str(userId)+"'"

        mycursor.execute(sql)

        myresult = mycursor.fetchall()
        data=[]
        for d in myresult:
            data.append(d["admin_id"])

        return data


    @staticmethod 
    def getChatsByIdList(ids:list, returnDic=True):
        res={}
        if(not returnDic):
            res=[]
        
        if(not len(ids)):
            return res
        
        idsStr=_convertListToSqlList(ids)


        mycursor = mydb.cursor(dictionary=True)
        sql="SELECT * from chats where id IN "+idsStr        
        mycursor.execute(sql)

        myresult = mycursor.fetchall()

        if(returnDic):
            for data in myresult:
                res[str(data["id"])]=data
        else:
            res=myresult

        return res
        


class UserConnector:
    @staticmethod
    def setUserOnline(userId):
        mycursor = mydb.cursor()

        sql = "UPDATE users SET last_seen = 'online' WHERE id = '"+str(userId)+"'"

        mycursor.execute(sql)

        mydb.commit()

        return "online"

    @staticmethod
    def setUserOffline(userId):
        mycursor = mydb.cursor()
        time_on=int(time.time())

        sql = "UPDATE users SET last_seen = '"+str(time_on)+"' WHERE id = '"+str(userId)+"'"

        mycursor.execute(sql)

        mydb.commit()

        return time_on


class EndPoints:

    @staticmethod
    def sendMsg(userID, chatID, msg, resId):
        return MessageConnector.sendDirectMsg(userID, chatID, msg, resId)

    @staticmethod
    def getChatData(id):
        return ChatConnector.getChatByid(id)
    
    @staticmethod
    def setChatAdmin(id, admin_id):
        return ChatConnector.setChatAdmin(id, admin_id)
    
    @staticmethod
    def setUseOnlineStatus(userId, isOnline):
        if(isOnline):
            return UserConnector.setUserOnline(userId)
        else:
            return UserConnector.setUserOffline(userId)

    @staticmethod
    def getAllUserToPing(userID, isAdmin):
        if(isAdmin):
            return ChatConnector.getUserIdsConnectedAdminAndOnline(userID)
        else:
            return ChatConnector.getAdminIdsConnectedUserAndOnline(userID)
        
    @staticmethod
    def markMessagesFromChatAsDelivered(chatID:int, msgIds_str, userID:int, time_del):
        MessageConnector.markMessagesFromChatAsDelivered(chatID, msgIds_str, userID, time_del)

    @staticmethod
    def markMessagesFromChatAsSeen(chatID:int, msgIds_str, userID:int, time_del):
        MessageConnector.markMessagesFromChatAsSeen(chatID, msgIds_str, userID, time_del)


    @staticmethod 
    def getChatsByIdList(ids:list, returnDic=True):
        return ChatConnector.getChatsByIdList(ids, returnDic)
    
    @staticmethod
    def getMessageByid(id, reconnect=False):
        return MessageConnector._getMsgById(id, reconnect)