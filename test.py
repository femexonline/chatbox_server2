from db_endpoints import EndPoints
import time
import json

chatData={
    3:"1_",
    "9":"5_3",
    19:"30_",
}


data=EndPoints.setUserOffline(2, 0)


print(data)


