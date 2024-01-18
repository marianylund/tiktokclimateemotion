import requests
from pathlib import Path
import pandas as pd
from tiktokfunctions import get_authorization_key, save_dict_as_csv, fromTimeStampToDate, save_json_to_file, generate_start_and_end_dates

# PARAMETERS
hashtags = ["climateanxiety", "ecoanxiety", "climatedoom", "climatedoomism", "climategrief", "climateoptimism", "ecoguilt", "klimaangst"] # Can define several hashtags ["hastag1", "hashtag2"] and it will find videos that match one or all of the tags
number_of_videos = 150000 # maximum number of videos to get per 30 days
total_start_date = "20200101" # "YYYYMMDD" in UTC including
total_end_date = "20231012" # "YYYYMMDD" in UTC including

# If set to random cannot continue search from the same curson or search_id
is_random = False # if set to True, then the API returns 1 - 100 videos in random order that matches the query. If set to False or not set with any value, then the API returns results in the decreasing order of video IDs.
num_vid_per_file = 10000  # Set the threshold for parsing

# ---------------------- CODE DO NOT CHANGE---------------------------
def query_videos(cursor, hashtags, number_of_videos, start_date, end_date, is_random, search_id):
    # Define the URL
    url = "https://open.tiktokapis.com/v2/research/video/query/?fields=id,video_description,hashtag_names,create_time,view_count,like_count,share_count,comment_count,region_code"

    # Define the headers
    headers = {
        "Authorization": "Bearer " + get_authorization_key(),
        "Content-Type": "application/json",
    }

    # Define the request data as a dictionary
    data = {
        "query": {
            "and": [
                {
                    "operation": "IN",
                    "field_name": "hashtag_name",
                    "field_values": hashtags
                }
            ],
        },
        "max_count": number_of_videos,
        "cursor": cursor,
        "start_date": start_date,
        "end_date": end_date,
        "is_random": is_random,
        "search_id": search_id
    }

    # Perform the POST request
    response = requests.post(url, headers=headers, json=data)
    return response

def parse_video_response(json_videos, cursor, foldername):
    videos = []
    for video in json_videos:
        link = f"https://www.tiktok.com/@username/video/{video['id']}" # tiktok still manages to open the video without the correct username
        videos.append({
            "id": video["id"],
            "create_time": fromTimeStampToDate(video["create_time"]),
            "video_description": video["video_description"],
            "hashtag_names": video["hashtag_names"],
            "region_code": video.get("region_code", None),        
            "comment_count": video.get("comment_count", 0),    
            "like_count": video.get("like_count", 0),          
            "view_count": video.get("view_count", 0),          
            "share_count": video.get("share_count", 0),        
            "link": link
        })
    save_dict_as_csv(videos, cursor, foldername, False)

videos = []  # List to accumulate videos
number_of_videos_saved = 0
foldername = total_start_date + total_end_date + "videos" # here you can change the filename or add something, remember to write inside "", so "someothername"
for start_date, end_date in generate_start_and_end_dates(total_start_date, total_end_date):
    success = True
    cursor = 0
    search_id = ""
    continue_to_query = True
    while(continue_to_query):
        get_number_of_videos = min(100, max(1, number_of_videos - cursor))
        response = query_videos(cursor, hashtags, get_number_of_videos, start_date, end_date, is_random, search_id)
        try:
            if(response == None):
                raise Exception("Response was None")

            response_json = response.json()
            # Check if the request was successful (status code 200)
            if response.status_code != 200:
                continue_to_query = False
                success = False
                raise Exception(f"Request failed with status code {response.status_code} on cursor {cursor} with search id: {search_id}")
        
            # Accumulate videos
            if(len(response_json["data"]["videos"]) == 0):
                continue_to_query = False
                print(f"No videos in the interval {start_date} to {end_date}, skipping")
            else:
                videos.extend(response_json["data"]["videos"])
                print(f'({response_json["data"]["cursor"]}/{number_of_videos}) has more: {response_json["data"]["has_more"]}')

                cursor = response_json["data"]["cursor"]
                continue_to_query = response_json["data"]["has_more"] and cursor < number_of_videos
                search_id = response_json["data"]["search_id"]

                # Check if you've accumulated 1000 videos and reset the count
                if len(videos) >= num_vid_per_file:
                    num_of_vid = len(videos)
                    parse_video_response(videos, f"{end_date}_{num_of_vid}", foldername)
                    number_of_videos_saved = number_of_videos_saved + len(videos)
                    print(f'Saved {num_of_vid} videos, has more: {response_json["data"]["has_more"]}, cursor: {response_json["data"]["cursor"]}')
                    videos = []  # Clear the list

        except Exception as e:
            continue_to_query = False
            success = False
            save_json_to_file(response_json, "error_" + foldername)
            if(len(videos) > 0):
                save_json_to_file(videos, "unsavedvideos_" + foldername)
            print("The error is: ", e.with_traceback)
            print(f"Got exception on cursor {cursor} with search id: {search_id}, start_date: {start_date}, end_date: {end_date}, {len(videos)} unsaved videos")

    if success:
        print(f"Finished getting {cursor} videos with search id: {search_id}")
    else:
        print("Failed.")
        break

# Check if you've accumulated 1000 videos and reset the count
num_of_vid = len(videos)
if num_of_vid > 0:
    parse_video_response(videos, f"{end_date}_{num_of_vid}", foldername)
    number_of_videos_saved = number_of_videos_saved + num_of_vid
    print(f'Parsed {num_of_vid} videos, has more: {response_json["data"]["has_more"]}, cursor: {response_json["data"]["cursor"]}')

print("Finished, in total saved " + str(number_of_videos_saved) + " videos")


# TODO: Should run this when all videos are downloaded
def add_index_to_data():
    # Specify your path here
    path = Path('data//2020010120231012videos_total')
    global_index = 0  # Global index for all records across files

    # Loop through all csv files
    for file in path.glob('*.csv'):
        # Read the csv file
        df = pd.read_csv(file)
        # Use regular expression to remove letters after @
        df['video_description'] = df['video_description'].str.replace('@\w+', '@', regex=True)
        # Write the dataframe back to csv
        # Create new index column
            # Create new index column
        index_col = range(global_index, global_index + len(df))
        global_index += len(df)  # Update the global index

        # Insert 'index' column at the first position
        df.insert(0, 'index', index_col)
        df.to_csv(file, index=False)