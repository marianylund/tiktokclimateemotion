import os
import pandas as pd
import shutil

# Load the CSV file with video IDs
csv_file_path = 'data\\2020010120231012_2000_0_.csv'  # Replace with the path to your CSV file
# Specify the source folder and destination folder
source_folder = 'data\\comments'  # Replace with the path to your source folder
destination_folder = 'data\\filtered_comments'  # Replace with the path to your destination folder


df = pd.read_csv(csv_file_path)

not_found = []
# Iterate through the video IDs in the CSV file
for video_id, index in zip(df['id'], df["index"]):
    # Construct the source file path and destination file path
    source_file = os.path.join(source_folder, f'{video_id}.csv')
    destination_file = os.path.join(destination_folder, f'{index}.csv')

     # Check if the destination folder exists and create it if it doesn't
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    # Check if the source file exists and copy it to the destination folder
    if os.path.exists(source_file):
        
        shutil.copy(source_file, destination_file)
        print(f'Copied {source_file} to {destination_file}')
    else:
        not_found.append(str(video_id))
        print(f'Source file {source_file} not found.')

print('Copy operation completed.')
if(len(not_found) > 0):
    print("Could not find comments for video ids:\n" + ", ".join(not_found))