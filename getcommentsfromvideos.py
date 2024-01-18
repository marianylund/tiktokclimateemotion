import csv
import requests
from pathlib import Path
import json
from tiktokfunctions import save_dict_as_csv, fromTimeStampToDate, get_authorization_key, save_json_to_file


# for now max 100, in total only top 1000 comments will be returned
number_of_comments = 999 # cannot be more than 999
video_file_path = Path("data\\2020010120231012_2000_0_climateanxietyecoanxiety.csv") # Add path to the file

num_com_per_file = 10000  # Set the threshold for parsing

# ---------------------- CODE DO NOT CHANGE---------------------------
# Initialize a list to store the video_ids
video_ids = []
video_file_name = video_file_path.stem

# Read existing comments for a video to skip
def get_filenames_in_folder(folder_path):
    folder_path = Path(folder_path)  # Convert the input path to a Path object
    if not folder_path.is_dir(): # Nothing to skip
        return []

    filenames = [file.stem for file in folder_path.iterdir() if file.is_file()]
    return filenames

video_ids_to_skip = get_filenames_in_folder("data/comments")

# Read data from the CSV file
with open(video_file_path, mode="r", newline='', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    
    # Iterate through rows in the CSV file and extract the 'id' field
    for row in reader:
        comment_count = int(row['comment_count'])
        video_id = row['id']
        if comment_count > 0:
            video_ids.append(video_id)
        else:
            print("Skipped video with id " + video_id + " because it has 0 comments")

def query_comments(cursor, number_of_comments, video_id):
     # Define the URL
    url = "https://open.tiktokapis.com/v2/research/video/comment/list/?fields=id,reply_count,like_count,create_time,text,video_id,parent_comment_id"

    # Define the headers
    headers = {
        "Authorization": "Bearer " + get_authorization_key(),
        "Content-Type": "application/json",
    }

    # Define the request data as a dictionary
    data = {
        "video_id": video_id,
        "max_count": number_of_comments,
        "cursor": cursor
    }

    # Convert the data dictionary to JSON
    data_json = json.dumps(data)
    # Perform the POST request
    response = requests.post(url, headers=headers, data=data_json)
    return response

def parse_comments_response(json_comments, filename, foldername):
    comments = []
    for comment in json_comments:
        comments.append({"id": comment["id"], "create_time": fromTimeStampToDate(comment["create_time"]), "text": comment["text"], 
        "reply_count": comment["reply_count"], 
        "like_count": comment["like_count"], "parent_comment_id": comment["parent_comment_id"]})

    save_dict_as_csv(comments, filename, foldername, False)

def get_comments_from_video(number_of_comments, video_id, comments_file_name):
    # Define the URL
    url = "https://open.tiktokapis.com/v2/research/video/comment/list/?fields=id,reply_count,like_count,create_time,text,video_id,parent_comment_id"

    # Define the headers
    headers = {
        "Authorization": "Bearer " + get_authorization_key(),
        "Content-Type": "application/json",
    }

    # Define the request data as a dictionary
    data = {
        "video_id": video_id,
        "max_count": 10,
        "cursor": 0
    }

    # Convert the data dictionary to JSON
    data_json = json.dumps(data)
    print(f"Getting comments with data: {json.dumps(data, indent=4)}")

    # Perform the POST request
    response = requests.post(url, headers=headers, data=data_json)

    # Parse the response as JSON and print it
    response_json = response.json()    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("Success getting response, parsing data")
        comments = []
        for comment in response_json["data"]["comments"]:
            comments.append({"id": comment["id"], "create_time": fromTimeStampToDate(comment["create_time"]), "text": comment["text"], 
            "reply_count": comment["reply_count"], 
            "like_count": comment["like_count"], "parent_comment_id": comment["parent_comment_id"]})

        save_dict_as_csv(comments, comments_file_name, "comments")
    else:
        print(f"Request failed with status code {response.status_code}")
        print(json.dumps(response_json, indent=4))

number_of_comments_saved = 0
video_ids_skipped = []
video_ids = [id for id in video_ids if id not in video_ids_to_skip] # filter out all video_ids that you have not gotten yet
for video_id in video_ids:
    comments = []  # List to accumulate comments
    folder_name = "comments"
    success = True
    cursor = 0
    continue_to_query = True
    while(continue_to_query):
        get_number_of_comments = min(100, max(1, number_of_comments - cursor))
        response = query_comments(cursor, get_number_of_comments, video_id)
        try:
            if(response == None):
                raise Exception("Response was None")

            response_json = response.json()

            # Check if the request was successful (status code 200)
            if response.status_code != 200:
                if(response_json["error"]["code"] == "internal_error"):
                    video_ids_skipped.append(video_id)
                    print("Skipping because of internal error: " + video_id)
                    continue
                elif(response_json["error"]["code"] == "timeout"):
                    video_ids_skipped.append(video_id)
                    print("Skipping because of timeout error: " + video_id)
                    continue
                continue_to_query = False
                success = False
                raise Exception(f"Request failed with status code {response.status_code} for video {video_id} on cursor {cursor}")
        
            # Accumulate comments
            if(len(response_json["data"]["comments"]) == 0):
                continue_to_query = False
                print(f"No comments for video {video_id}, skipping")
            else:
                comments.extend(response_json["data"]["comments"])
                print(f'({response_json["data"]["cursor"]}/{number_of_comments}) has more: {response_json["data"]["has_more"]}')

                cursor = response_json["data"]["cursor"]
                continue_to_query = response_json["data"]["has_more"] and cursor < number_of_comments

                # Check if you've accumulated 1000 comments and reset the count
                if len(comments) >= num_com_per_file:
                    num_of_com = len(comments)
                    parse_comments_response(comments, f"{video_id}", folder_name)
                    number_of_comments_saved = number_of_comments_saved + len(comments)
                    print(f'Saved {num_of_com} comments, has more: {response_json["data"]["has_more"]}, cursor: {response_json["data"]["cursor"]}')
                    comments = []  # Clear the list

        except Exception as e:
            continue_to_query = False
            success = False
            save_json_to_file(response_json, f"error_{folder_name}_{video_id}")
            if(len(comments) > 0):
                save_json_to_file(comments, f"unsavedcomments_{folder_name}_{video_id}")
            print("The error is: ", str(e))
            print(f"Got exception on cursor {cursor}, {len(comments)} unsaved videos")

    if success:
        print(f"Finished getting {cursor} comments")
        num_of_com = len(comments)
        if num_of_com > 0:
            parse_comments_response(comments, f"{video_id}", folder_name)
            number_of_comments_saved = number_of_comments_saved + len(comments)
            print(f'Saved {num_of_com} comments, has more: {response_json["data"]["has_more"]}, cursor: {response_json["data"]["cursor"]}')
    else:
        print("Failed.")
        break

print("Finished, in total saved " + str(number_of_comments_saved) + " comments")
print(f"Skipped {len(video_ids_skipped)} videos because of internal error: " + str(video_ids_skipped))




