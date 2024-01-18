import pandas as pd
import json
import csv
from datetime import datetime, timedelta
from pathlib import Path 
import re
import os
from dotenv import load_dotenv

def get_authorization_key():
    if not load_dotenv():
        raise FileNotFoundError("No .env file found or the file is empty. Please create one and try again.")
    TIKTOK_KEY = os.getenv('TIKTOK_KEY')
    if TIKTOK_KEY is None:
        raise ValueError("TIKTOK_KEY not found in .env file. Please add it to the file and try again.")
    return TIKTOK_KEY


def fromTimeStampToDate(timestamp):
    # Convert the timestamp to a datetime object
    date_time = datetime.utcfromtimestamp(timestamp)

    # Format the datetime object as "dd.mm.yyyy"
    formatted_date = date_time.strftime("%d.%m.%Y")

    return formatted_date

def generate_start_and_end_dates(start_date, end_date, interval = 30):
    # Convert the start_date and end_date strings to datetime objects
    start_date_obj = datetime.strptime(start_date, "%Y%m%d")
    end_date_obj = datetime.strptime(end_date, "%Y%m%d")

    # Initialize lists to store the dates
    start_dates = []
    end_dates = []

    # Define the interval (30 days)
    interval = timedelta(days=interval)

    # Initialize the current date
    current_date = start_date_obj

    # Generate the dates with at most 30-day intervals
    while current_date <= end_date_obj:
        start_dates.append(current_date.strftime("%Y%m%d"))
        next_date = current_date + interval
        end_dates.append(min(next_date, end_date_obj).strftime("%Y%m%d"))
        current_date = next_date + timedelta(days=1)

    # Example usage:
    print("Generated " + str(len(start_date)) + " date intervals between " + start_date + " and " + end_date)
    return zip(start_dates, end_dates)

def get_filenames_in_folder(folder_path):
    folder_path = Path(folder_path)  # Convert the input path to a Path object
    if not folder_path.is_dir():
        raise ValueError("The specified path is not a directory.")

    filenames = [file.stem for file in folder_path.iterdir() if file.is_file()]
    return filenames

def filter_videos(path_to_video_folder, save_to_file = False):
    # Define the folder where your CSV files are located
    folder_path = Path(path_to_video_folder)

    # Initialize an empty list to store DataFrames
    dataframes = []

    # Loop through CSV files in the folder
    for csv_file in folder_path.glob("*.csv"):
        # Read each CSV file into a DataFrame
        single_df = pd.read_csv(csv_file)
        dataframes.append(single_df)

    # Concatenate all DataFrames into one
    df = pd.concat(dataframes, ignore_index=True)
    df['create_time'] = pd.to_datetime(df['create_time'], format='%d.%m.%Y')
    filtered_df = df[((df['view_count'] > 2000) | (df['like_count'] > 2000)) & (df['comment_count'] > 0)]
    filtered_df = filtered_df.sort_values(by='view_count', ascending=False)
    # Calculate the average comment_count from the filtered DataFrame
    average_comment_count = filtered_df['comment_count'].mean()
    # Get the minimum and maximum 'create_time' values
    min_create_time = filtered_df['create_time'].min()
    max_create_time = filtered_df['create_time'].max()

    # Print the date range
    print(f"Date Range: {min_create_time} to {max_create_time}, average_comment_count: {average_comment_count}")
    if save_to_file:
        file_name = path_to_video_folder + "_over2000_over0comments"
        filtered_df.to_csv(Path(file_name), index=False)
    return filtered_df

def create_raw_data_from_video_descriptions(video_file_path_csv, subtract_hashtags=False):
    extracted_text = []
    with open(video_file_path_csv, mode="r", newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            text = row.get("video_description", "")
            if subtract_hashtags:
                # Subtract the hashtags in the 'hashtag_names' list from the 'video_description'
                hashtags_string = row.get("hashtag_names", "")
                # Use regular expression to extract hashtags in square brackets and single quotes
                hashtags = re.findall(r"'(.*?)'", hashtags_string)
                # Split the text into words and filter out hashtags
                words = text.split()
                filtered_words = [word for word in words if word.lower() not in ['#' + tag.lower() for tag in hashtags]]
                # Reconstruct the text from the filtered words
                text = " ".join(filtered_words)
            if text:
                extracted_text.append(text)

    output_file = video_file_path_csv.with_suffix(".txt")
    # Check if there is any text to write
    if extracted_text:
        # Combine the text and save it to the output file
        with open(output_file, "w", encoding='utf-8') as text_file:
            for text in extracted_text:
                text_file.write(text + "\n")

        print(f"Extracted text saved to {output_file}")
    else:
        print("No text extracted from the comments CSV files.")
    return output_file

def create_raw_text_data_from_comments():
    # Path to the directory containing your CSV files
    comments_folder = Path.cwd() / "data" / "comments"  # Replace with the actual folder path
    if not comments_folder.is_dir():
        raise FileNotFoundError(f"The folder '{comments_folder}' does not exist. Remember to run getcommentsfromvideos.py first to gather comments from videos.")

    # Path to the output text file
    output_file = comments_folder / "rawtextdata.txt"

    # Initialize an empty list to store the extracted text
    extracted_text = []

    # Iterate through CSV files in the folder
    for csv_file in comments_folder.glob("*.csv"):
        with open(csv_file, mode="r", newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                text = row.get("text", "")
                if text:
                    extracted_text.append(text)

    # Check if there is any text to write
    if extracted_text:
        # Combine the text and save it to the output file
        with open(output_file, "w", encoding='utf-8') as text_file:
            for text in extracted_text:
                text_file.write(text + "\n")

        print(f"Extracted text saved to {output_file}")
    else:
        print("No text extracted from the comments CSV files.")
    return output_file

def save_json_to_file(json_data, filename):
    with open(filename + ".json", "w", encoding='utf-8') as outfile:
            # Serializing json
            json_videos = json.dumps(json_data, indent=4)
            outfile.write(json_videos)
            print("Saved to " + filename + ".json file")

def save_dict_as_csv(data_dict, filename, folder = "", debug_log = True):
    # Extract fieldnames from the keys of the first dictionary
    if not data_dict:
        raise ValueError("data_dict is empty. Make sure it contains data.")
    fieldnames = list(data_dict[0].keys())
    folder_path = Path.cwd() / "data" / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    # Create the full path to the CSV file
    csv_file_path = folder_path / (str(filename) + ".csv")

    # Save the data to a CSV file
    with open(csv_file_path, mode="w", newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write the data rows
        writer.writerows(data_dict)

    if(debug_log):
        print("Saved data to " + str(csv_file_path) + " file")