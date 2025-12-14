import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
import plotly.express as px


API_KEY = "AIzaSyAX1Evyg2vqnCkQgW7eLrkgCY9xbJ29nYY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build(
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    developerKey=API_KEY
)

st.set_page_config(page_title="YouTube Data Dashboard", layout="wide")


def get_channel_stats(channel_id):
    request = youtube.channels().list(
        part="statistics,snippet",
        id=channel_id
    )
    response = request.execute()

    stats = response["items"][0]["statistics"]
    snippet = response["items"][0]["snippet"]

    return {
        "Channel Name": snippet["title"],
        "Subscribers": int(stats["subscriberCount"]),
        "Total Views": int(stats["viewCount"]),
        "Total Videos": int(stats["videoCount"])
    }


def get_video_data(channel_id, max_results=20):
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video"
    )
    response = request.execute()

    video_ids = [item["id"]["videoId"] for item in response["items"]]

    video_request = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    )
    video_response = video_request.execute()

    data = []
    for item in video_response["items"]:
        data.append({
            "Title": item["snippet"]["title"],
            "Views": int(item["statistics"].get("viewCount", 0)),
            "Likes": int(item["statistics"].get("likeCount", 0)),
            "Comments": int(item["statistics"].get("commentCount", 0))
        })

    return pd.DataFrame(data)


st.title("YouTube Data Dashboard")

channel_id = st.text_input("Enter YouTube Channel ID")

if channel_id:
    with st.spinner("Fetching data..."):
        channel_stats = get_channel_stats(channel_id)
        video_df = get_video_data(channel_id)

   
    st.subheader(" Channel Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Subscribers", channel_stats["Subscribers"])
    col2.metric("Total Views", channel_stats["Total Views"])
    col3.metric("Total Videos", channel_stats["Total Videos"])

   
    st.subheader(" Filter Videos")
    min_views = st.slider("Minimum Views", 0, int(video_df["Views"].max()), 0)
    filtered_df = video_df[video_df["Views"] >= min_views]


    st.subheader(" Top Performing Videos (Views)")
    fig1 = px.bar(
        filtered_df.sort_values("Views", ascending=False),
        x="Views",
        y="Title",
        orientation="h",
        color="Views"
    )
    st.plotly_chart(fig1, use_container_width=True)

   
    st.subheader(" Engagement Metrics")
    fig2 = px.scatter(
        filtered_df,
        x="Views",
        y="Likes",
        size="Comments",
        hover_name="Title"
    )
    st.plotly_chart(fig2, use_container_width=True)

    
    st.subheader(" Video Data")
    st.dataframe(filtered_df)
