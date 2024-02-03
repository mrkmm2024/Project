**Project Title **                      : YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit
**Skills take away From This Project ** : Python scripting, Data Collection,MongoDB, Streamlit, API integration, Data Management using MongoDB (Atlas) and SQL  
**Domain **                             : Social Media
	
**Problem Statement:**
The problem statement is to create a Streamlit application that allows users to access and analyze data from multiple YouTube channels. The application should have the following features:
1. Ability to input a YouTube channel ID and retrieve all the relevant data (Channel name, subscribers, total video count, playlist ID, video ID, likes, dislikes, comments of each video) using Google API.
2. Option to store the data in a MongoDB database as a data lake.
3. Ability to collect data for up to 10 different YouTube channels and store them in the data lake by clicking a button.
4. Option to select a channel name and migrate its data from the data lake to a SQL database as tables.
5. Ability to search and retrieve data from the SQL database using different search options, including joining tables to get channel details.

**Approach: **
1. Set up a Streamlit app: Streamlit is a great choice for building data visualization and analysis tools quickly and easily. You can use Streamlit to create a simple UI where users can enter a YouTube channel ID, view the channel details, and select channels to migrate to the data warehouse.
2. Connect to the YouTube API: You'll need to use the YouTube API to retrieve channel and video data. You can use the Google API client library for Python to make requests to the API.
3. Store data in a MongoDB data lake: Once you retrieve the data from the YouTube API, you can store it in a MongoDB data lake. MongoDB is a great choice for a data lake because it can handle unstructured and semi-structured data easily.
4. Migrate data to a SQL data warehouse: After you've collected data for multiple channels, you can migrate it to a SQL data warehouse. You can use a SQL database such as MySQL or PostgreSQL for this.
5. Query the SQL data warehouse: You can use SQL queries to join the tables in the SQL data warehouse and retrieve data for specific channels based on user input. You can use a Python SQL library such as SQLAlchemy to interact with the SQL database.
6. Display data in the Streamlit app: Finally, you can display the retrieved data in the Streamlit app. You can use Streamlit's data visualization features to create charts and graphs to help users analyze the data.
Overall, this approach involves building a simple UI with Streamlit, retrieving data from the YouTube API, storing it in a MongoDB data lake, migrating it to a SQL data warehouse, querying the data warehouse with SQL, and displaying the data in the Streamlit app.

**SQL Query Output need to displayed as table in Streamlit Application:**

1.	What are the names of all the videos and their corresponding channels?
2.	Which channels have the most number of videos, and how many videos do
 they have?
3.	What are the top 10 most viewed videos and their respective channels?
4.	How many comments were made on each video, and what are their
 corresponding video names?
5.	Which videos have the highest number of likes, and what are their 
corresponding channel names?
6.	What is the total number of likes and dislikes for each video, and what are 
their corresponding video names?
7.	What is the total number of views for each channel, and what are their 
corresponding channel names?
8.	What are the names of all the channels that have published videos in the year
 2022?
9.	What is the average duration of all videos in each channel, and what are their 
corresponding channel names?
10.	Which videos have the highest number of comments, and what are their 
corresponding channel names?

**Results: **
This project aims to develop a user-friendly Streamlit application that utilizes the Google API to extract information on a YouTube channel, stores it in a MongoDB database, migrates it to a SQL data warehouse, and enables users to search for channel details and join tables to view data in the Streamlit app.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**Technology Stack Used:**

1. Python
2. google.apiv3.python
3. MongodB(Atlas)
4. MySQL
5. Streamlit
6. Jupyter notebook

**Security And Compliances.**
1. The youtoube API is restricted to access onyl public data in ready only mode.
2. MongoDB is configured with X509 certificate.
3. The API keys and other crendentials are imported via config.py.

**Summary**
1. Create the Application framework using Streamlit
2. Scrape the data using Google youtube API.
3. import the semistructured/unstructured data to MonogoDB ( Atlas )
4. import the dataframe ( structured data ) to SQL DB
5. Analysis the data in sql and ans the list of 10 Question

**Steps to consume the code in Git Hub.**
1. Clone the code.
2. update the API's/Mongodb/SqlDB urls respectively
3. update the credentials
4. excute frontend.py via streamlit.
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                                                                                           **Screen shots** 
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Installing dependent Python Modules.
--------------------------------------
![image](https://github.com/mrkmm2024/Project/assets/157888294/aef339e5-5a88-4fb8-9a55-85e05e364cd4)

Testing Google youtube API Authentication:
--------------------------------------------------
![image](https://github.com/mrkmm2024/Project/assets/157888294/aa236595-10de-4a92-b143-fab256397787)

Mongodb
-----------
![image](https://github.com/mrkmm2024/Project/assets/157888294/f2e404a7-39eb-460a-866a-cc5b59b08e8e)

Data_load_MongoDB
-----------------
![image](https://github.com/mrkmm2024/Project/assets/157888294/46d4abe9-b84c-4e1c-a543-f24af14eca01)

Data Import to SQL DB
--------------------------------
![image](https://github.com/mrkmm2024/Project/assets/157888294/a3166061-9a3b-4ef6-8395-bee171d90a51)
Data Analysis:
--------------------
![image](https://github.com/mrkmm2024/Project/assets/157888294/a3114565-9de3-4025-bd2d-7d6dd9d58541)
