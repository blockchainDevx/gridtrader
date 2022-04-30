import os
from datetime import datetime
import pytz

list1=[]
list2=[]
i=0

with open('./log.csv',encoding='utf-8') as file_obj:
    for line in file_obj:
        if i%2==0:
            list2.append(line)
        list1.append(line)
        i=i+1

timestamp1=datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%b %d %Y %H:%M:%S.%f, ")
print(timestamp1)
list3= list(set(list2)^set(list1))
timestamp1=datetime.now(pytz.timezone('Asia/Shanghai')).strftime("%b %d %Y %H:%M:%S.%f, ")
print(timestamp1)
print(len(list1))
print(len(list2))
print(len(list3))
     
