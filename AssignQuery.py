import mysql.connector
import QueryServiceProvider
import pandas as pd

try:
    con = QueryServiceProvider.getConnection()
    cursor=con.cursor()
    #status='CLOSED'
    status='OPENED'
    queries=QueryServiceProvider.getUnAssignedQueryByStatus(cursor,status)
    suppUser=QueryServiceProvider.fetchUserWithType(cursor,2)
    print('No. of queries:',queries.__len__())
    suppCount=suppUser.__len__()
    print('No. of users:',suppCount)
    tile=int(queries.__len__()/suppCount)

    splitResult=QueryServiceProvider.getUnAssignedQueryByStatusWithTile(cursor,status,suppCount)

    for i in range(1,suppCount+1):
        perSuppList=[]
        for row in splitResult:
            if(row[1]==i):
                perSuppList.append((suppUser[i-1][0],row[0]))
        print(f'For user {i}-> - list of query assigned:: {perSuppList}')
        QueryServiceProvider.updateQueryWithSuppId(cursor,perSuppList)
        
    con.commit()
            


except mysql.connector.Error as err:
    print(f"Error in:: {err}")
finally:
    if 'con' in locals() and con.is_connected():
        con.close()
        print("Connection closed")