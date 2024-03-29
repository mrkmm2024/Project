import googleapiclient
from googleapiclient.discovery import build
import config
import mysql.connector
from mysql.connector import Error
import streamlit as st
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd


st.set_page_config(page_title='Youtube_data', page_icon = 'https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png', layout= "wide")
page_bg_img = """
<style>
[data-testid="stAppViewContainer"] {
background-image: url("https://cdn.pixabay.com/photo/2014/06/16/23/39/black-370118_640.png");
background-size: cover;
}

</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.header(':rainbow[YOUTUBE DATA HARVESTING AND WAREHOUSING] :milky_way:')


#  Authenticating to Google youtube API
@st.cache_data
def youtube_api_authenticate():
    Api_id = config.apikey
    Api_service_name = "youtube"
    Api_version = "v3"
    youtube = build(Api_service_name,Api_version,developerKey = Api_id)
    return youtube


# Extracting youtube channel list
@st.cache_data
def get_channel_details(_youtube, **kwargs):
    return youtube.channels().list(
        part="statistics,snippet,contentDetails",
        **kwargs
    ).execute()

# Extracting Playlist Details
@st.cache_data
def get_playlist_details(_youtube, **kwargs):
    return youtube.playlists().list(
        part="snippet,contentDetails",
        **kwargs,
        maxResults=50
    ).execute()

# Extracting playlist items details
@st.cache_data
def get_playlistitems_details(_youtube, pl_id):
    return youtube.playlistItems().list(
        part="snippet,contentDetails",
        maxResults=50,
        playlistId=pl_id
    ).execute()

# Extracting video details
@st.cache_data
def get_video_details(_youtube, **kwargs):
    return youtube.videos().list(
        part="snippet,contentDetails,statistics",
        maxResults=50,
        **kwargs
    ).execute()

# Extracting comment details
@st.cache_data
def get_comment_details(_youtube, video_id):
    return youtube.commentThreads().list(
        part="snippet,replies",
        maxResults=50,
        videoId=video_id
    ).execute()

# Feeding the scraped data to MonogoDB
# Push channel details to MongoDB
def channel_details_to_mongo_db(data):
    ch_details = {
        "channelTitle": data['items'][0]['snippet']['title'],
        "channelId": data['items'][0]['id'],
        "subscriberCount": data['items'][0]['statistics']['subscriberCount'],
        "channel_viewCount": data['items'][0]['statistics']['viewCount'],
        "channel_description": data['items'][0]['snippet']['description'],
        "videoCount": data['items'][0]['statistics']['videoCount'],
        "playlist_details": playlist_details_to_mongo_db(data['items'][0]['id'])

    }

    channel_db.insert_one(ch_details)

# push playlist and playlist item details to MongoDB
def playlist_details_to_mongo_db(channel_id):
    pl_of_ch_id = get_playlist_details(youtube, channelId=channel_id)
    pl_det = []

    for i in pl_of_ch_id['items']:
        pl_id = i['id']
        pl_item_det = get_playlistitems_details(youtube, pl_id)
        # playlistitem_details_to_mongo_db(pl_id)
        pl_items = []
        for j in pl_item_det['items']:
            pl_items.append({'channelId': j['snippet']['channelId'],
                             'channelTitle': j['snippet']['channelTitle'],
                             'playlistId': j['snippet']['playlistId'],
                             'videoId': j['contentDetails']['videoId'],
                             'Video_details': video_details_to_mongo_db(j['contentDetails']['videoId'])
                             })
        playlistitems_db.insert_many(pl_items)
        pl_det.append({
            'playlistId': i['id'],
            'channelId': i['snippet']['channelId'],
            'playlistTitle': i['snippet']['title'],

            'Playlist_video_count': i['contentDetails']['itemCount'],
            'playlistitem_details': pl_items
        })

    playlist_det = playlist_db.insert_many(pl_det)
    return playlist_det.inserted_ids

# push video details to MongoDB
def video_details_to_mongo_db(v_id):
    video_det = get_video_details(youtube, id=v_id)

    for each_item in video_det['items']:
        try:

            vid_details = {
                'videoId': each_item['id'],
                'video_publishedAt': each_item['snippet']['publishedAt'],
                'channelId': each_item['snippet']['channelId'],
                'video_title': each_item['snippet']['title'],
                'video_description': each_item['snippet']['description'],
                'thumbnail_url': each_item['snippet']['thumbnails']['default']['url'],
                'channelTitle': each_item['snippet']['channelTitle'],
                'duration': each_item['contentDetails']['duration'],
                'viewCount': each_item['statistics']['viewCount'],
                'likeCount': each_item['statistics']['likeCount'],
                'favoriteCount': each_item['statistics']['favoriteCount'],
                'commentCount': each_item['statistics']['commentCount'],
                'commentDetails': comment_details_to_mongo_db(each_item['id'])

            }

        except:
            vid_details = {
                'videoId': each_item['id'],
                'video_publishedAt': each_item['snippet']['publishedAt'],
                'channelId': each_item['snippet']['channelId'],
                'video_title': each_item['snippet']['title'],
                'video_description': each_item['snippet']['description'],
                'thumbnail_url': each_item['snippet']['thumbnails']['default']['url'],
                'channelTitle': each_item['snippet']['channelTitle'],
                'duration': each_item['contentDetails']['duration'],
                'viewCount': each_item['statistics']['viewCount'],
                'likeCount': -1,
                'favoriteCount': each_item['statistics']['favoriteCount'],
                'commentCount': -1,
                'commentDetails': 'Not Available'
            }

        video = video_db.insert_one(vid_details)
        return video.inserted_id

# Push comment details to mongoDB
def comment_details_to_mongo_db(vid_id):
    comm_details = get_comment_details(youtube, vid_id)
    comments = []

    for i in comm_details['items']:
        comments.append({
            'commentId': i['id'],
            'videoId': i['snippet']['topLevelComment']['snippet']['videoId'],
            'textDisplay': i['snippet']['topLevelComment']['snippet']['textDisplay'],
            'authorDisplayName': i['snippet']['topLevelComment']['snippet']['authorDisplayName'],
            'publishedAt': i['snippet']['topLevelComment']['snippet']['publishedAt']
        })
    comment = comment_db.insert_many(comments)
    return comment.inserted_ids
    
# function to convert duration
def convert_duration(each_item):
    if each_item.__contains__('H'):
        if each_item.__contains__('M'):
            if each_item.__contains__('S'):
                hours = int(each_item[2:].split('H')[0])
                minutes = int(each_item[2:].split('H')[1].split('M')[0])
                total_seconds = int(each_item[2:].split('M')[1][:-1]) + (minutes * 60) + (hours * 60 * 60)
                return total_seconds
            else:
                hours = int(each_item[2:].split('H')[0])
                minutes = int(each_item[2:-1].split('H')[1])
                return (hours * 60 * 60 + minutes * 60)
        elif each_item.__contains__('S'):
            hours = int(each_item[2:].split('H')[0])
            total_seconds = int(each_item[2:].split('H')[1][:-1]) + (hours * 60 * 60)
            return total_seconds
        else:
            hours = int(each_item[2:-1])
            return hours * 60 * 60
    elif each_item.__contains__('M'):
        if each_item.__contains__('S'):
            minutes = int(each_item[2:].split('M')[0])
            total_seconds = int(each_item[2:].split('M')[1][:-1]) + (minutes * 60)
            return total_seconds
        else:
            minutes = int(each_item[2:].split('M')[0])
            return minutes * 60
    else:
        return int(each_item[2:-1])



if __name__ == "__main__":
    youtube = youtube_api_authenticate()

    user_input_channel_ids = []
    channels = {}
    playlist = {}
    playlist_ids = {}
    playlistitems = {}
    video_details = {}
    comment_details = {}
    
    with st.sidebar:
         st.sidebar.header(":wave: :violet[**Youtube Data Scrapping**]")
         st.sidebar.caption("Using channel id we can fetch data from youtube upto 10 Channels...")
         st.sidebar.subheader("Data Collection")
         number = st.sidebar.number_input('**Select Number of Channels**', value=1, min_value=1, max_value=10)
         for i in range(number):
            user_input_channel_ids.append(st.sidebar.text_input("**ENTER NEW CHANNEL ID**", key=i))
         if st.sidebar.button(":green[Scrape Data]"):
             st.sidebar.write("Processing...")
            # Create a new client and connect to the server
             # MongoDB connection made secure using x.509 certificate  
             uri = "mongodb+srv://cluster0.mrnioqs.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
             client = MongoClient(uri,
                                  tls=True,
                                  tlsCertificateKeyFile=r'F:\GUVI\Project\X509-cert-4411951663520314148.pem')

        # Sending a ping to confirm a successful connection
             try:
                 client.admin.command('ping')
                 st.sidebar.write("Connected to MongoDB!")
             except Exception as e:
                 st.sidebar.write(e)
        # creating/selecting database and collections
             yt_dbs = client['yt_dbs']
             channel_db = yt_dbs['channels']
             playlist_db = yt_dbs['playlists']
             playlistitems_db = yt_dbs['playlistitems']
             video_db = yt_dbs['videodetails']
             comment_db = yt_dbs['comments']

             channel_db.delete_many({})
             playlist_db.delete_many({})
             playlistitems_db.delete_many({})
             video_db.delete_many({})
             comment_db.delete_many({})

             for each_id in user_input_channel_ids:
                 channel_details_to_mongo_db(get_channel_details(youtube, id=each_id))

             st.write(":green[Completed successfully.]")
             
         else:
            st.write("click on 'Scrape Data' to get data")

st.title(':red[Data in MongoDB]')
if __name__ == "__main__":
  
    uri = "mongodb+srv://cluster0.mrnioqs.mongodb.net/?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
    client = MongoClient(uri,
                         tls=True,
                         tlsCertificateKeyFile=r'F:\GUVI\Project\X509-cert-4411951663520314148.pem')
    try:
        client.admin.command('ping')
    except Exception as e:
        st.write(e)

    yt_dbs = client['yt_dbs']
    channel_db = yt_dbs['channels']
    playlist_db = yt_dbs['playlists']
    playlistitems_db = yt_dbs['playlistitems']
    video_db = yt_dbs['videodetails']
    comment_db = yt_dbs['comments']

    # channel df creation
    channels_df = pd.DataFrame(list(channel_db.find({}, {'_id': 0, 'playlist_details': 0})))
    
    # playlist df creation
    playlist_df = pd.DataFrame(list(playlist_db.find({}, {'_id': 0, 'playlistitem_details': 0})))
    pl_items_df = pd.DataFrame(list(playlistitems_db.find({}, {'_id': 0, 'Video_details': 0})))
    # video details to dataframe
    video_df = pd.DataFrame(list(video_db.find({}, {'_id': 0, 'commentDetails': 0})))
    video_df['video_publishedAt'] = pd.to_datetime(video_df['video_publishedAt'])
    video_df['duration'] = video_df['duration'].apply(lambda row: convert_duration(row))
    video_df = video_df.merge(pl_items_df, how='inner')

    # comment details to dataframe
    comment_df = pd.DataFrame(list(comment_db.find({}, {'_id': 0})))
    comment_df['publishedAt'] = pd.to_datetime(comment_df['publishedAt'])
    final_df = channels_df.merge(playlist_df, how='left')
    final_df = final_df.merge(video_df, how='right', on=['playlistId', 'channelTitle', 'channelId'])
    final_df = final_df.merge(comment_df, how='left', on='videoId')

    dropdown = []

    for each_ch_name in channels_df['channelTitle']:  # to find the channel names from mongo db
        dropdown.append(each_ch_name)
    # creating a dropdown
    options = st.multiselect(
        ":green[**Select the channels which you want see details and load to SQL**]",
        tuple(dropdown))


    for option in options:

        try:
            a = SQL_channel_details_df.head()
        except:
            SQL_channel_details_df = pd.DataFrame()

        SQL_channel_details_df = pd.concat([SQL_channel_details_df, channels_df[channels_df['channelTitle'] == option]])

        try:
            b = SQL_plalist_df.head()
        except:
            SQL_plalist_df = pd.DataFrame()

        # CHANNEL_ID=channels_df[channels_df['Channel_Name']==option].index[0]

        SQL_plalist_df = pd.concat([SQL_plalist_df, playlist_df[
            playlist_df['channelId'] == (channels_df[channels_df['channelTitle'] == option]['channelId'].values[0])]])

        try:
            c = SQL_video_df.head()
        except:
            SQL_video_df = pd.DataFrame()
        try:
            d = SQL_comments_df.head()
        except:
            SQL_comments_df = pd.DataFrame()

        for each_pl_id in set(SQL_plalist_df['playlistId']):
            SQL_video_df = pd.concat([SQL_video_df, video_df[video_df['playlistId'] == each_pl_id]])

        for each_v_id in set(SQL_video_df['videoId']):
            SQL_comments_df = pd.concat([SQL_comments_df, comment_df[comment_df['videoId'] == each_v_id]])

        SQL_channel_details_df.reset_index(inplace=True, drop=True)
        SQL_plalist_df.reset_index(inplace=True, drop=True)
        SQL_video_df = SQL_video_df.drop_duplicates(subset=['videoId'])
        SQL_video_df.reset_index(inplace=True, drop=True)
        SQL_comments_df = SQL_comments_df.drop_duplicates(subset=['commentId'])
        SQL_comments_df.reset_index(inplace=True, drop=True)
        # Show output as dataframes in streamlit
        show_table = st.radio(":blue[SELECT THE TABLE FOR VIEW]",(":blue[CHANNELS]",":blue[PLAYLISTS]",":blue[VIDEOS]",":blue[COMMENTS]"))

        if show_table ==":blue[CHANNELS]":
           st.header(":blue[Channel Details]")
           st.dataframe(SQL_channel_details_df)

        elif show_table ==":blue[PLAYLISTS]":
             st.header(":blue[Playlist Details]")
             st.dataframe(SQL_plalist_df)

        elif show_table == ":blue[VIDEOS]":
             st.header(":blue[Video Details]")
             st.dataframe(SQL_video_df)

        elif show_table ==":blue[COMMENTS]":
             st.header(":blue[Comments Details]")
             st.dataframe(SQL_comments_df)



# codes to migrate data from MongoDB to SQL
st.title(':red[Data Migration]')
if st.button(":green[Import to SQL DB]"):
    import mysql.connector
    from mysql.connector import Error
    try:
        mydb = mysql.connector.connect(host="localhost",
                                       database='youtube_data',
                                       user="root",
                                       password=config.sqlpwd,
                                       port=3306)
        if mydb.is_connected():
            db_Info = mydb.get_server_info()
            st.write("Connected to MySQL Server version ", db_Info)
            cursor = mydb.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            st.write("You're connected to database: ", record)
            cursor.execute("drop table if exists comment_det")
            cursor.execute("drop table if exists video_det")
            cursor.execute("drop table if exists playlist_det")
            cursor.execute("drop table if exists channel_det")

            cursor.execute(
                    "create table if not exists channel_det(Channel_Name VARCHAR(255),Channel_Id VARCHAR(255) PRIMARY KEY,Subscription_Count INT,Channel_Views BIGINT,Channel_Description TEXT,Number_of_Videos INT)")
            cursor.execute(
                    "create table if not exists playlist_det(playlist_id VARCHAR(255) PRIMARY KEY, Channel_id VARCHAR(255), FOREIGN KEY (Channel_id) REFERENCES channel_det(Channel_Id), Playlist_title VARCHAR(255), Playlist_video_count INT)")
            cursor.execute(
                    "create table if not exists video_det(video_id VARCHAR(255) PRIMARY KEY, video_publishedAt VARCHAR(255), Channel_id VARCHAR(255), video_title TEXT, Video_description TEXT,thumbnail_url VARCHAR(255), channelTitle VARCHAR(255), duration INT, viewCount INT, likeCount INT,favoriteCount INT, commentCount INT, playlist_id VARCHAR(255), FOREIGN KEY (playlist_id) REFERENCES playlist_det(playlist_id))")
            cursor.execute(
                    "create table if not exists comment_det(comment_id VARCHAR(255) PRIMARY KEY, video_id VARCHAR(255), FOREIGN KEY (video_id) REFERENCES video_det(video_id),textDisplay TEXT, authorDisplayName VARCHAR(255),publishedAt VARCHAR(255))")

            for each_row in range(len(SQL_channel_details_df)):
                val = tuple(SQL_channel_details_df.loc[each_row])
                sql = "insert into channel_det values (%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, val)
                mydb.commit()

            for each_row in SQL_plalist_df.index:
                val = tuple(SQL_plalist_df.values[each_row])
                sql = "insert into playlist_det values (%s,%s,%s,%s)"
                cursor.execute(sql, val)
                mydb.commit()

            for each_row in SQL_video_df.index:
                val = tuple(SQL_video_df.values[each_row])
                sql = "insert into video_det values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, val)
                mydb.commit()

            for each_row in SQL_comments_df.index:
                val = tuple(SQL_comments_df.values[each_row])
                sql = "insert into comment_det values (%s,%s,%s,%s,%s)"
                cursor.execute(sql, val)
                mydb.commit()

            st.write(":green[Finished loading details to SQL database]")
            st.write("navigate to next page in sidebar to proceed")

    except Error as e:
        st.write("Error while connecting to MySQL", e)
        st.write("click 'Import to SQL database' to load the filtered data")


# codes for answering all the questions
# if st.button(":green[Data Analysis]"):
st.title(":red[Data Analysis]")
if __name__ == "__main__":
    try:
        mydb = mysql.connector.connect(host="localhost",
                                       database='youtube_data',
                                       user="root",
                                       password=config.sqlpwd,
                                       port=3306)
        if mydb.is_connected():
            db_Info = mydb.get_server_info()
            st.write()
            cursor = mydb.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            st.write(":green[Connected to MySQL Server version :]", db_Info , ":green[Database is :]", record)
            SQL_question = st.selectbox('**Select your Question from dropdown**',
                                        ('',
                                         '1. What are the names of all the videos and their corresponding channels?',
                                         '2. Which channels have the most number of videos, and how many videos do they have?',
                                         '3. What are the top 10 most viewed videos and their respective channels?',
                                         '4. How many comments were made on each video, and what are their corresponding video names?',
                                         '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                                         '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                                         '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                                         '8. What are the names of all the channels that have published videos in the year 2023?',
                                         '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                                         '10. Which videos have the highest number of comments, and what are their corresponding channel names?'),
                                        key='collection_question')
            if SQL_question == '1. What are the names of all the videos and their corresponding channels?':
                Q1 = "SELECT video_det.video_title, video_det.ChannelTitle FROM video_det LEFT JOIN playlist_det ON video_det.playlist_id=playlist_det.playlist_id"
                ans1 = pd.read_sql(Q1, mydb)
                st.write(ans1)
                st.write("Select next question and see the details")

            if SQL_question == '2. Which channels have the most number of videos, and how many videos do they have?':
                cursor.execute("SELECT Channel_name, Number_of_Videos FROM channel_det ORDER BY Number_of_Videos DESC")
                ans2 = cursor.fetchall()
                df2 = pd.DataFrame(ans2, columns=['Channel_name', 'Number_of_Videos']).reset_index(drop=True)
                df2.index += 1
                st.dataframe(df2)
                st.write("Select next question and see the details")

            if SQL_question == '3. What are the top 10 most viewed videos and their respective channels?':
                a = pd.read_sql("SELECT Channel_Name FROM channel_det", mydb)
                channels_list = []
                for i in range(len(a)):
                    channels_list.append(a.loc[i].values[0])

                ans3 = pd.DataFrame()
                for each_channel in channels_list:
                    Q3 = f"SELECT * FROM video_det WHERE channelTitle='{each_channel}' ORDER BY viewCount DESC LIMIT 10"
                    ans3 = pd.concat([ans3, pd.read_sql(Q3, mydb)], ignore_index=True)
                st.write(ans3[['video_title', 'channelTitle', 'viewCount']])
                st.write("Select next question and see the details")

            if SQL_question == '4. How many comments were made on each video, and what are their corresponding video names?':
                Q4 = "SELECT video_det.video_title, video_det.video_id,count(comment_det.comment_id) AS no_of_comments FROM video_det LEFT JOIN comment_det ON video_det.video_id=comment_det.video_id group by video_id"
                ans4 = pd.read_sql(Q4, mydb)
                st.write(ans4)
                st.write("Select next question and see the details")

            if SQL_question == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
                Q5 = "SELECT video_det.video_title, video_det.likeCount,channel_det.Channel_Name FROM video_det LEFT JOIN playlist_det ON video_det.playlist_id=playlist_det.playlist_id LEFT JOIN channel_det ON channel_det.Channel_Id=playlist_det.Channel_id ORDER BY video_det.likeCount DESC"
                ans5 = pd.read_sql(Q5, mydb)
                st.write(ans5)
                st.write("Select next question and see the details")

            if SQL_question == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
                Q6 = "SELECT video_det.video_title,video_det.likeCount FROM video_det ORDER BY video_det.likeCount DESC LIMIT 10"
                ans6 = pd.read_sql(Q6, mydb)
                st.write(ans6)
                st.write("Select next question and see the details")

            if SQL_question == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
                Q7 = "SELECT channel_det.Channel_Name,channel_det.Channel_Views FROM channel_det"
                ans7 = pd.read_sql(Q7, mydb)
                st.write(ans7)
                st.write("Select next question and see the details")

            if SQL_question == '8. What are the names of all the channels that have published videos in the year 2023?':
                Q8 = "SELECT video_det.video_title,video_det.channelTitle,video_det.video_publishedAt FROM video_det WHERE YEAR(video_publishedAt) = 2023"
                ans8 = pd.read_sql(Q8, mydb)
                st.write(ans8)
                st.write("Select next question and see the details")

            if SQL_question == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
                Q9 = "SELECT video_det.channelTitle, sum(video_det.duration)/count(video_det.video_id) AS average_duration_in_seconds FROM video_det group by video_det.channelTitle"
                ans9 = pd.read_sql(Q9, mydb)
                st.write(ans9)
                st.write("Select next question and see the details")

            if SQL_question == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
                Q10 = 'SELECT count(comment_det.comment_id) AS no_of_comments, video_det.video_title AS name_of_video,video_det.channelTitle FROM video_det LEFT JOIN comment_det ON comment_det.video_id=video_det.video_id GROUP BY video_det.video_title,video_det.channelTitle ORDER BY no_of_comments DESC LIMIT 10'
                ans10 = pd.read_sql(Q10, mydb)
                st.write(ans10)

                st.write("Thank you for using my App")

    except Error as e:
        st.write("Error while connecting to MySQL", e)
