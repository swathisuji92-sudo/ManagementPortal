import mysql.connector
import datetime

def saveUser(cursor,name,email,userTypeId,mobile,encrPwd):
    currTime=datetime.datetime.now()
    query=f"insert into user (user_name,mail_id,user_type_id,create_time,update_time,mobile_number,pswrd) value ('{name}','{email}',{userTypeId},'{currTime}','{currTime}',{mobile},'{encrPwd}')"
    cursor.execute(query)

def saveQuery(cursor,query_sub_type_id,client_user_id,query_status,raised_time,closed_time,update_time):
    query=f"insert into query (query_sub_type_id,client_user_id,query_status,raised_time,closed_time,update_time) value ({query_sub_type_id},{client_user_id},'{query_status}','{raised_time}','{closed_time}','{update_time}')"
    cursor.execute(query)

def saveOpenQuery(cursor,query_sub_type_id,client_user_id,query_status,raised_time,update_time,blob):
    query=f"insert into query (query_sub_type_id,client_user_id,query_status,raised_time,update_time,image) value (%s,%s,%s,%s,%s,%s)"
    cursor.execute(query, (query_sub_type_id,client_user_id,query_status,raised_time,update_time,blob))

def saveOpenQueryWOImg(cursor,query_sub_type_id,client_user_id,query_status,raised_time,update_time):
    query=f"insert into query (query_sub_type_id,client_user_id,query_status,raised_time,update_time) value (%s,%s,%s,%s,%s)"
    cursor.execute(query, (query_sub_type_id,client_user_id,query_status,raised_time,update_time))

def getQueryTypeAndOccurence(cursor):
    query=f''' SELECT qt.query_type_name,qst.query_desc,count(q.query_id) as occurence FROM query q 
                join QUERY_SUB_TYPE qst ON q.query_sub_type_id=qst.query_sub_type_id 
                JOIN QUERY_TYPE qt ON qt.query_type_id=qst.query_type_id group by q.query_sub_type_id order by occurence desc '''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def updateQueryWithSuppId(cursor,query_supp_id):
    query=f"update query SET support_user_id = %s where query_id = %s"
    cursor.executemany(query,query_supp_id)

def updateUserCred(cursor,email,pwd):
    query=f"update user SET pswrd = '{pwd}' where mail_id = '{email}'"
    cursor.execute(query)

def updateQueryWithSuppUsrIdWithStatus(cursor,supp_user,status,query_id):
    currTime=datetime.datetime.now()
    query=''
    if status=="IN PROGRESS":
        query=f"update query SET support_user_id = {supp_user}, query_status='{status}', update_time='{currTime}' where query_id = {query_id}"
    elif status=="CLOSED":
        query=f"update query SET support_user_id = {supp_user}, query_status='{status}', update_time='{currTime}', closed_time='{currTime}'  where query_id = {query_id}"

    print(query)
    cursor.execute(query)

def updateQueryWithRating(cursor,rating,query_id):
    query=f"update query SET rating = {rating} where query_id = {query_id}"
    print(query)
    cursor.execute(query)

def getUnAssignedQueryByStatus(cursor,status):
    query=f"select * from query where upper(query_status) = '{str(status).upper()}' and support_user_id is NULL"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def getOpenQuery(cursor,status):
    query=f'''SELECT q.query_id,qt.query_type_name,qst.query_desc,q.query_status,q.raised_time,q.update_time, q.image FROM query q 
    join QUERY_SUB_TYPE qst ON q.query_sub_type_id=qst.query_sub_type_id JOIN QUERY_TYPE qt ON qt.query_type_id=qst.query_type_id
     where upper(q.query_status) = '{str(status).upper()}' '''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def getQueryCount(cursor,status):
    query=f'''SELECT count(q.query_id) FROM query q where upper(q.query_status) = '{str(status).upper()}' '''
    cursor.execute(query)
    return cursor.fetchone()

def getQueryByStatus(cursor,status):
    query=f'''SELECT q.query_id, qt.query_type_name,qst.query_desc,DATE(q.raised_time),DATE(q.closed_time) FROM query q 
    join QUERY_SUB_TYPE qst ON q.query_sub_type_id=qst.query_sub_type_id JOIN QUERY_TYPE qt ON qt.query_type_id=qst.query_type_id
     where upper(q.query_status) = '{str(status).upper()}' '''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def getAllQueries(cursor,status):
    query=f'''SELECT u.user_id,u.user_name,sum(q.rating) as rating FROM query q 
    join User u on q.support_user_id=u.user_id where q.query_status='{status}' GROUP BY q.support_user_id ORDER BY rating desc'''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def getQueryCountWithinTime(cursor,status,toDate,col):
    query=f'''SELECT count(query_id) FROM query where {col} > DATE("{toDate}") and upper(query_status) = '{str(status).upper()}' '''
    cursor.execute(query)
    return cursor.fetchone()


def getQueryRaisedByUser(cursor,userId):
    query=f'''SELECT q.query_id,qt.query_type_name,qst.query_desc,q.query_status,CASE WHEN support_user_id is NULL THEN '' 
    ELSE (SELECT user_name from USER where user_id=support_user_id) END as support ,q.raised_time,q.closed_time,CASE WHEN q.rating is NULL 
     THEN 0 ELSE q.rating END as rating, q.image FROM query q 
    join QUERY_SUB_TYPE qst ON q.query_sub_type_id=qst.query_sub_type_id JOIN QUERY_TYPE qt ON qt.query_type_id=qst.query_type_id
     where q.client_user_id ={userId}'''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def getQueryRaisedBySuppUser(cursor,suppUserId):
    query=f'''SELECT q.query_id, qt.query_type_name,qst.query_desc,q.query_status,q.raised_time,q.closed_time,q.image,
    CASE WHEN q.rating is NULL THEN 0 ELSE q.rating END as rating
    FROM query q join QUERY_SUB_TYPE qst ON q.query_sub_type_id=qst.query_sub_type_id 
    JOIN QUERY_TYPE qt ON qt.query_type_id=qst.query_type_id JOIN USER u ON u.user_id=q.support_user_id 
    where q.support_user_id ={suppUserId} order by q.query_status;'''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def getSupportLoad(cursor):
    query='''SELECT u1.user_name,CASE WHEN A.wip IS NULL THEN 0 ELSE A.wip END as wipCount from 
    (SELECT u.user_id as userId, u.user_name as userName,count(q.query_id) as wip FROM USER u 
    LEFT JOIN query q ON u.user_id=q.support_user_id where query_status='IN PROGRESS' group by q.support_user_id )
    AS A RIGHT JOIN `USER` u1 ON A.userId=u1.user_id where u1.user_type_id=2 order by wipCount desc;'''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def getUnAssignedQueryByStatusWithTile(cursor,status,tile):
    query=f"SELECT A.qId, A.tileNum FROM (select query_id AS qId, NTILE({tile}) OVER(ORDER BY query_id) AS tileNum FROM query where upper(query_status) = '{str(status).upper()}') AS A"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def getQueryType(cursor):
    query=f"select * from query_type"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def saveQuerySubType(cursor,query_type_id,query_desc):
    currTime=datetime.datetime.now()
    query=f"insert into query_sub_type (query_type_id,query_desc,create_time,update_time) value ({query_type_id},'{query_desc}','{currTime}','{currTime}')"
    cursor.execute(query)

def getQuerySubTypeByQueryIdDesc(cursor,query_type_id,query_desc):
    query=f"select * from query_sub_type where query_type_id = {query_type_id} and query_desc='{query_desc}'"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def getQuerySubTypeByQueryId(cursor,query_type_id):
    query=f"select * from query_sub_type where query_type_id = {query_type_id}"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def getAllQuerySubType(cursor):
    query=f"select * from query_sub_type"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def fetchUser(cursor,mail):
    fetchUserQuery=f"select * from user where lower(mail_id)=lower('{mail}')"
    cursor.execute(fetchUserQuery)
    rows = cursor.fetchall()
    return rows

def fetchUserWithTypePwd(cursor,mail,userType,pwd):
    validateUserQuery=f"select * from user where lower(mail_id)=lower('{mail}') and user_type_id={userType} and pswrd='{pwd}'"
    print(validateUserQuery)
    cursor.execute(validateUserQuery)
    row = cursor.fetchone()
    return row

def fetchUserWithType(cursor,userType):
    validateUserQuery=f"select * from user where user_type_id={userType}"
    cursor.execute(validateUserQuery)
    rows = cursor.fetchall()
    return rows


def getConnection():
    con = mysql.connector.connect(host="localhost",
                                    user="root",
                                    password="root@123",
                                    database="CLIENT_MANAGEMENT")
    return con