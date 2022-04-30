import pymysql

connect=pymysql.Connect(host='localhost',user='root',password='gridtrade',database='grid_datas')
cursor=connect.cursor(pymysql.cursors.DictCursor)
res=cursor.execute('select * from api_datas',{})
result = cursor.fetchall()
print(res, result)