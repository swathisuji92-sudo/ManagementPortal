# ManagementPortal
This repository has the code for query management of clients and support load, statistic discovery on queries 

Current Features:
1. Management Portal :
   cmd - streamlit run /Users/manikandan/Documents/Sujitha/vsCode_Proj/UserQueryManagement.py

   Pages and facilities:
   1. Client:
      a. Client can raise query with error screenshot
      b. Client can monitor the history of query status and rate the statisfaction score for support provided by executive member.
   2. Support:
      a. List of queries that are Open and In Progress will be displaced for the support team to pick it, along with screenshot of issue.
      b. No. of occurence of unique issue reported can be easily identified and looked for a common ETA and by specific person.
      c. Support person can view the list of queries fixed by own and the satisfaction score.
    3. Admin:
       a. This credential is capable of handling the load of support, inflow of queries and Rate at which query resolved.
       b. Admin can onboard user and reset their password on request.
       c. Stats page shows ETA for a common query type, Performance report on different timelines, Start performers in support, Most repeated queries, Current load of support team

3. Batch of queries (from csv file) can be loaded in database after cleansing on the email, contact in case of migration
   cmd - python BulkQueryLoad.py

4. Assign outstanding Query as per the support availability
   cmd - python AssignQuery.py

Future Scope:
1. As per support load, we can automate AssignQuery.py class to run in a defined frequency.
2. We can have automated tracker to check the sudden spike of any common issue and alert the Admin and support team.
3. Analysis can be performed on Least rated queries and find RCA
4. A bot can be placed to answer some repeated  self do able client queries OR ETA of Past query history
