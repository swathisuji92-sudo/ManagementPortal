import streamlit as st
import hashlib
import QueryServiceProvider
import pandas as pd
from datetime import datetime,timedelta,date
import mysql.connector
import re
import uuid
import io
import base64
from PIL import Image


if "screen" not in st.session_state:
    st.session_state.screen = ""

if "user" not in st.session_state:
    st.session_state.user = ""

if "userId" not in st.session_state:
    st.session_state.userId = ""

if "userType" not in st.session_state:
    st.session_state.userType = ""

if "queryStatus" not in st.session_state:
    st.session_state.queryStatus = False

if "cliTableStatus" not in st.session_state:
    st.session_state.cliTableStatus = False

if 'cliTab_key' not in st.session_state:
        st.session_state.cliTab_key = str(uuid.uuid4())

if 'suppTab_key' not in st.session_state:
    st.session_state.suppTab_key = str(uuid.uuid4())

if 'file_key' not in st.session_state:
    st.session_state.file_key=str(uuid.uuid4())

def logout():
    st.session_state.screen = ""
    st.session_state.user = ""
    st.session_state.userType = ""
    st.session_state.userId = ""
    st.session_state.queryStatus = False
    st.session_state.cliTableStatus = False
    st.rerun()

def loadSubQuery(cursor,queryId):
    subQueries=QueryServiceProvider.getQuerySubTypeByQueryId(cursor,queryId)
    return pd.DataFrame(subQueries)

def updateStatus():
    st.session_state.queryStatus=True

def updateCliTableStatus():
    st.session_state.cliTableStatus=True

def updateCliTableKey():
    st.session_state.cliTab_key=str(uuid.uuid4())

def updateSuppTableKey():
    st.session_state.suppTab_key=str(uuid.uuid4())

def updateFileKey():
    st.session_state.file_key=str(uuid.uuid4())

def validate(name,email,mobile,pwd):
    error = ''
    if len(name)==0 or len(name)>60 or not(re.fullmatch(r"^[A-Za-z0-9\s]+$",name)):
        error=error+' \n * Name is empty or allowed characters are alaphabets and space only'
    if len(email)==0 or not(re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',email)):
        error=error+' \n * Mail Id doesnt meet the expected pattern'
    if not(len(mobile)==10) or not(re.fullmatch(r"^[0-9]+$",mobile)):
        error=error+' \n * Mobile number doesnt meet length of 10 or has characters other than numbers'
    if len(pwd)<8 or pwd.find(' ') != -1 or pwd.find('*') != -1 or pwd.find('%') != -1 :
        error=error+' \n * Invalid password: Length has to be 8 or more and space, * , % not allowed'
    return error

def fireQueryForAnalysis(cursor):
    queriesAndOccurence=QueryServiceProvider.getQueryTypeAndOccurence(cursor)
    return pd.DataFrame(queriesAndOccurence,columns=['Query Category','Query SubCategory','Occurence'])

def fireQueryForSupportLoad(cursor):
    wipQueries=QueryServiceProvider.getSupportLoad(cursor)
    return pd.DataFrame(wipQueries,columns=['Support User','WIP Query Count'])

def blob_to_data_url(blob_data, image_type="image/png"):
    if blob_data:
        base64_encoded = base64.b64encode(blob_data).decode('utf-8')
        return f"data:{image_type};base64,{base64_encoded}"
    return None

st.set_page_config(layout="wide")

if st.session_state.screen=="":

    st.write('### ::::::::Welcome to Query Reporting Portal:::::::')

    #text_input_container=email_text_input_container=user_input_container=pwd_input_container = st.empty()
    #email_text_input_container= st.empty()
    #email=email_text_input_container.text_input('Enter Login Mail:')
    #userType=user_input_container.radio("Enter user type:",['Client','Support'])
    #pwd=pwd_input_container.text_input('Enter password')
    #loginSubmit=text_input_container.button('Login')
    email=st.text_input('Enter Login Mail:',key="email")
    userType=st.radio("Enter user type:",['Client','Support'])
    pwd=st.text_input('Enter password',key="pwd")
    loginSubmit=st.button('Login')


    if loginSubmit:
        userTypeId=0
        if email.startswith('admin'):
            userTypeId=3
        elif userType=='Client':
            userTypeId=1
        elif userType=='Support':
            userTypeId=2
        try:
            con = QueryServiceProvider.getConnection()
            cursor=con.cursor()
            encrPwd=hashlib.sha256(pwd.encode()).hexdigest()
            entry=QueryServiceProvider.fetchUserWithTypePwd(cursor,email,userTypeId,encrPwd)
            if entry:
                #note=f'### Welcome {entry[1]} !!!'
                #text_input_container.empty()
                #email_text_input_container.empty()
                #user_input_container.empty()
                #pwd_input_container.empty()
                st.info(f'### Welcome {entry[1]} !!!')
                st.session_state.screen = "Home"
                st.session_state.user = entry[1]
                st.session_state.userId = entry[0]
                st.session_state.userType = entry[3]
                st.rerun()
                
            else:
                st.error('Invalid User/Password')
        except mysql.connector.Error as err:
                print(f"Error in:: {err}")
        finally:
                if 'con' in locals() and con.is_connected():
                    con.close()
                    print("Connection closed")

elif st.session_state.screen =="Home":
    st.write('''-----------------------------------''')
    st.write(f"###         Query Management Portal ")
    st.button("Logout",on_click=logout)
    st.write('''-----------------------------------''')
    st.write(f"### Welcome to Home Page {st.session_state.user} !!!")
    if st.session_state.userType==1:
        tab1, tab2 = st.tabs(["Report Issue", "Query History"])
        try:
            con = QueryServiceProvider.getConnection()
            cursor=con.cursor()
            with tab1:
                queries=QueryServiceProvider.getQueryType(cursor)
                queryDF=pd.DataFrame(queries)
                queryOptions=[queryDF[1],queryDF[0]]
                selectedQuery=st.selectbox(label="Select Query Type",options=queryOptions[0])
                #loadSubQuery(cursor,queryOptions[0]==selectedQuery)
                selectedQueryId=queryDF[queryDF[1]==selectedQuery][0].to_list()
                subQueryDF=loadSubQuery(cursor,selectedQueryId[0])
                subQueryOptions=[subQueryDF[2],subQueryDF[0]]
                selectedSubQuery=st.selectbox(label="Select Sub Type",options=subQueryOptions[0])
                with st.form("queryForm", clear_on_submit=True):
                    error_img = st.file_uploader("Give an error Screenshot:", type=["png"],key=st.session_state.file_key)
                    querySubmit=st.form_submit_button('Submit')
                    if querySubmit:
                        #st.markdown(':green[Query has been submitted. Ideal response time is 4hrs to get back. \n Please check ''Query History'' tab for updates.]')
                        st.success('Query has been submitted. Ideal response time is 4hrs to get back. \n Please check ''Query History'' tab for updates.')
                        selectedSubQueryId=subQueryDF[subQueryDF[2]==selectedSubQuery][0].to_list()
                        if error_img is not None:
                            blob=error_img.getvalue()
                            QueryServiceProvider.saveOpenQuery(cursor,selectedSubQueryId[0],st.session_state.userId,'OPENED',
                                                datetime.now(),datetime.now(),blob)  
                            updateFileKey()                      
                        else:
                            QueryServiceProvider.saveOpenQueryWOImg(cursor,selectedSubQueryId[0],st.session_state.userId,'OPENED',
                                                datetime.now(),datetime.now())

                        con.commit()
            with tab2:
                result=QueryServiceProvider.getQueryRaisedByUser(cursor,st.session_state.userId)
                clientDf=pd.DataFrame(result,columns=['Query Id','Query Type','Query Description','Query Status','Support User','Raised Time','Closed Time', 'Satisfaction Rate', 'Error Image'])
                clientDf['Error Image']=clientDf.apply(lambda x : blob_to_data_url(x['Error Image'], "image/png"), axis=1)
                #clientDf["Satisfaction Rate"]=clientDf.apply(lambda x : int(x["Satisfaction Rate"]) if x["Satisfaction Rate"]>0 else int(0), axis=1)
                editRatingDf=st.data_editor(clientDf, key=st.session_state.cliTab_key, column_config={
                        "Satisfaction Rate": st.column_config.NumberColumn(
                            "Satisfaction Rate",
                            help="Select 5 to 1. 5 is Highly Satisifed & 1 is Least Satisfied",
                            min_value=0,
                            max_value=5,
                            step=1,
                            format="%d ⭐",
                        ),
                        'Error Image': st.column_config.ImageColumn('Error Image', width="medium",help="Click to view"),
                        'Query Id': None,
                    }, on_change=updateCliTableStatus,)

                if st.session_state.cliTableStatus:
                    status_changed=clientDf.ne(editRatingDf)
                    status_changed=editRatingDf[status_changed['Satisfaction Rate'].gt(0)]
                    for i in status_changed.iterrows():
                        print(i[1].iloc[7],"---",i[1].iloc[0],"---",i[1].iloc[3])
                        if str(i[1].iloc[3])=="CLOSED":
                            QueryServiceProvider.updateQueryWithRating(cursor,int(i[1].iloc[7]),i[1].iloc[0])
                    con.commit()
                    st.session_state.cliTableStatus=False
                    updateCliTableKey()
                    st.rerun()
        except mysql.connector.Error as err:
                print(f"Error in:: {err}")
        finally:
                if 'con' in locals() and con.is_connected():
                    con.close()
                    print("Connection closed")
        con.close()
    elif st.session_state.userType==2:
        try:
            con = QueryServiceProvider.getConnection()
            cursor=con.cursor()
            tab1, tab2 = st.tabs(["Outstanding Query Board", "Queries Owned"])
            with tab1:
                openQueries=QueryServiceProvider.getOpenQuery(cursor, "OPENED")
                df=pd.DataFrame(openQueries,columns=['Query Id','Query Type','Query Description','Query Status','Raised Time','Updated Time', 'Error Image'])
                inProgQueries=QueryServiceProvider.getOpenQuery(cursor, "IN PROGRESS")
                inProgQueriesDF=pd.DataFrame(inProgQueries,columns=['Query Id','Query Type','Query Description','Query Status','Raised Time','Updated Time', 'Error Image'])
                mergedDF=pd.concat([df,inProgQueriesDF])
                mergedDF['Error Image']=mergedDF.apply(lambda x : blob_to_data_url(x['Error Image'], "image/png"), axis=1)

                edited_df = st.data_editor(
                    mergedDF,key=st.session_state.suppTab_key,
                    column_config={
                        "Query Status": st.column_config.SelectboxColumn(
                            "Query Status",
                            help="Select the item's status",
                            width="medium",
                            options=["OPENED", "IN PROGRESS", "CLOSED"],
                            required=True,
                        ),
                        'Error Image': st.column_config.ImageColumn('Error Image', width="medium",help="Click to view"),
                    }, on_change=updateStatus,disabled=['Query Id','Query Type','Query Description','Raised Time','Updated Time', 'Error Image']
                ,hide_index=True)
                bool_status_changed=mergedDF.ne(edited_df)
                bool_status_changed=edited_df[bool_status_changed['Query Status'].eq(True)]

                if st.session_state.queryStatus:
                    for i in bool_status_changed.iterrows():
                        QueryServiceProvider.updateQueryWithSuppUsrIdWithStatus(cursor,st.session_state.userId,i[1][3],i[1][0])
                    con.commit()
                    st.session_state.queryStatus=False
                    updateSuppTableKey()
                    st.rerun()
            with tab2:
                con = QueryServiceProvider.getConnection()
                cursor=con.cursor()
                suppHist=QueryServiceProvider.getQueryRaisedBySuppUser(cursor,st.session_state.userId)
                suppHistDf=pd.DataFrame(suppHist,columns=['Query Id','Query Type','Query Description','Query Status','Raised Time','Closed Time','Error Screenshot','Satisfaction Rate'])
                suppHistDf['Error Screenshot']=suppHistDf.apply(lambda x : blob_to_data_url(x['Error Screenshot'], "image/png"), axis=1)
                st.data_editor(suppHistDf,column_config={
                        'Error Screenshot': st.column_config.ImageColumn('Error Screenshot', width="medium",help="Click to view"),
                        "Satisfaction Rate": st.column_config.NumberColumn(
                            "Satisfaction Rate",
                            help="Select 5 to 1. 5 is Highly Satisifed & 1 is Least Satisfied",
                            min_value=0,
                            max_value=5,
                            step=1,
                            format="%d ⭐",
                        ),
                    },disabled=True,hide_index=True)
        
        except mysql.connector.Error as err:
                print(f"Error in:: {err}")
        finally:
                if 'con' in locals() and con.is_connected():
                    con.close()
                    print("Connection closed")

        con.close()
    elif st.session_state.userType==3:
        con = QueryServiceProvider.getConnection()
        cursor=con.cursor()
        tab1, tab2 = st.tabs(["User OnBoard/Cred Reset", "Quert Portal Data Insights"])
        with tab1:
            st.write('### User onboarding:')
            name=st.text_input('Enter user Name:', max_chars=60)
            email=st.text_input('Enter user EMAIL:')
            mobile=st.text_input('Enter 10 digit mobile number:', max_chars=10)
            userType=st.radio("Enter user type:",['Client','Support','Admin'])
            enrollPwd=st.text_input('Enter password',key="enrollPwd")
            submit=st.button('Add User')
            if submit:
                if userType=='Client':
                    userTypeId=1
                elif userType=='Support':
                    userTypeId=2
                else:
                    userTypeId=3
                msg=validate(name,email,mobile,enrollPwd)
                if len(msg)==0:
                    encrPwd=hashlib.sha256(enrollPwd.encode()).hexdigest()
                    print(name,email,mobile,encrPwd)
                    try:
                        con = QueryServiceProvider.getConnection()
                        cursor=con.cursor()
                        entry=QueryServiceProvider.fetchUser(cursor,email)
                        if len(entry)==0:
                            QueryServiceProvider.saveUser(cursor,name,email,userTypeId,mobile,encrPwd)
                            con.commit()
                            st.info('User added successfully')
                        else:
                            st.warning('User already exists')
                    except mysql.connector.Error as err:
                        print(f"Error in:: {err}")
                    finally:
                        if 'con' in locals() and con.is_connected():
                            con.close()
                            print("Connection closed")
                else:
                    st.error(msg)
            resetSubmit=st.button('Reset User Password')
            if resetSubmit:
                if len(enrollPwd)<8 or enrollPwd.find(' ') != -1 or enrollPwd.find('*') != -1 or enrollPwd.find('%') != -1 :
                    st.error('* Invalid password: Length has to be 8 or more and space, * , % not allowed')
                if len(email)==0:
                    st.error('* Email is mandatory for Password reset')
                else:
                    encrPwd=hashlib.sha256(enrollPwd.encode()).hexdigest()
                    try:
                        con = QueryServiceProvider.getConnection()
                        cursor=con.cursor()
                        entry=QueryServiceProvider.fetchUser(cursor,email)
                        if len(entry)!=0:
                            QueryServiceProvider.updateUserCred(cursor,email,encrPwd)
                            con.commit()
                            st.success('User password updated successfully')
                        else:
                            st.error('User not exists')
                    except mysql.connector.Error as err:
                        print(f"Error in:: {err}")
                    finally:
                        if 'con' in locals() and con.is_connected():
                            con.close()
                            print("Connection closed")
            st.markdown(''' :red[* Email and Password mandatory for credential reset] ''')
        with tab2:
            st.write('### Select on which topic insights needed:')
            analOption = st.selectbox("Pick the area where analysis is needed",
                                  ("Most frequent queries", "Average ETA for each query type", "Support Team Load", "Star performers in Support", "Support Performance Report"),
                                  index=None,placeholder="------------------Select------------------")
            try:
                con = QueryServiceProvider.getConnection()
                cursor=con.cursor()
                if analOption=="Most frequent queries":
                    queryOccDf=fireQueryForAnalysis(cursor)
                    st.dataframe(queryOccDf)
                    st.write('### Pictorial view:')
                    st.bar_chart(queryOccDf, x="Occurence", y="Query SubCategory", color="Query Category")
                
                elif analOption=="Support Team Load":
                    openQueryCount=QueryServiceProvider.getQueryCount(cursor,"OPENED")
                    ipQueryCount=QueryServiceProvider.getQueryCount(cursor,"IN PROGRESS")
                    st.write(f'## No. of Open queries = {openQueryCount[0]}')
                    st.write(f'## No. of InProgress queries = {ipQueryCount[0]}')
                    wipDF=fireQueryForSupportLoad(cursor)
                    st.dataframe(wipDF)
                
                elif analOption=="Support Performance Report":
                    freq = st.selectbox("Pick the period for which report is needed",
                                  ("Yesterday", "Last Week", "Last 30 days","Last 90 days"),index=None,placeholder="-------Select-------")
                    noOfInProgQuery=[0]
                    noOfCloseQuery=[0]
                    noOfOpenQuery=[0]
                    presentDay=datetime.today().date()
                    toDate=presentDay
                    if freq=="Yesterday":
                        toDate=presentDay - timedelta(days=1)
                    elif freq=="Last Week":
                        toDate=presentDay - timedelta(days=7)
                    elif freq=="Last 30 days":
                        toDate=presentDay - timedelta(days=30)
                    elif freq=="Last 90 days":
                        toDate=presentDay - timedelta(days=90)
                    noOfInProgQuery=QueryServiceProvider.getQueryCountWithinTime(cursor,"IN PROGRESS",toDate,"update_time")
                    noOfCloseQuery=QueryServiceProvider.getQueryCountWithinTime(cursor,"CLOSED",toDate,"closed_time")
                    noOfOpenQuery=QueryServiceProvider.getQueryCountWithinTime(cursor,"OPENED",toDate,"raised_time")

                    st.write(f'## No. of Closed queries since "{freq}" = {noOfCloseQuery[0]}')
                    st.write(f'## No. of In Progress queries since "{freq}" = {noOfInProgQuery[0]}')
                    st.write(f'## No. of Open queries since "{freq}" = {noOfOpenQuery[0]}')
                    countData = {
                        'Status': ['Closed','In Progress','Open'],
                        'Count of Queries':[noOfCloseQuery[0],noOfInProgQuery[0],noOfOpenQuery[0]]
                    }
                    countDF=pd.DataFrame(countData)
                    st.line_chart(countDF,x="Status",y="Count of Queries")
                elif analOption=="Average ETA for each query type":
                    records=QueryServiceProvider.getQueryByStatus(cursor,"CLOSED")
                    recDf=pd.DataFrame(records,columns=['Query Id','Query Type','Query Description','Raised Date','Closed Date'])
                    recDf['Average days']=recDf.apply(lambda x : ((date(int(str(x['Closed Date']).split("-")[0]), int(str(x['Closed Date']).split("-")[1]), int(str(x['Closed Date']).split("-")[2])))
                        -(date(int(str(x['Raised Date']).split("-")[0]), int(str(x['Raised Date']).split("-")[1]), int(str(x['Raised Date']).split("-")[2])))).days,axis=1)
                    avgETABySubQuery=recDf.groupby(['Query Description','Query Type'])['Average days'].mean()
                    st.dataframe(avgETABySubQuery)
                elif analOption=="Star performers in Support":
                    bestPerf=QueryServiceProvider.getAllQueries(cursor,'CLOSED')
                    bestPerfDF=pd.DataFrame(bestPerf,columns=['ID','User','Satisfactory Score'])
                    st.dataframe(bestPerfDF,hide_index=True)

            except mysql.connector.Error as err:
                print(f"Error in:: {err}")
            finally:
                if 'con' in locals() and con.is_connected():
                    con.close()
                    print("Connection closed")



            
            
        
        

    

