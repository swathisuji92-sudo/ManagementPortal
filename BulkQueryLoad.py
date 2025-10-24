import pandas as pd
import mysql.connector
import QueryServiceProvider
from datetime import datetime

#bulkOnBoardFilePath=str(input('Give file path for Bulk OnBoard:'))
bulkOnBoardFilePath="/Users/manikandan/Documents/Sujitha/vsCode_Proj/synthetic_client_queries.csv"
data=pd.read_csv(bulkOnBoardFilePath)
df=pd.DataFrame(data)

print(df['query_description'].nunique())

# for i in uniqSubQueryList.iterrows:
#     df.query("select * from ")

uniqSubQueryList=df.groupby('query_description').head(1)

try:
    con = QueryServiceProvider.getConnection()
    cursor=con.cursor()
    queryType=QueryServiceProvider.getQueryType(cursor)
    queryDict={}

    for row in queryType:
        queryDict[row[1]]=row[0]
    
    for i in uniqSubQueryList.values:
        print(f"{i[3]} ---- {i[4]}")
        desc=str(i[4]).replace("'","''")
        entry=QueryServiceProvider.getQuerySubTypeByQueryIdDesc(cursor,queryDict[i[3]],desc)
        if len(entry)==0:
            QueryServiceProvider.saveQuerySubType(cursor,queryDict[i[3]],desc)
        else:
            print('Sub Query already exists')
    con.commit()

except mysql.connector.Error as err:
    print(f"Error in:: {err}")
finally:
    if 'con' in locals() and con.is_connected():
        con.close()
        print("Connection closed")

#print(uniqSubQueryList)
