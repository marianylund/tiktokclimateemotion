import pandas as pd
from pathlib import Path
import ast

# Define the folder where your CSV files are located
folder_path = Path("data\\2020010120231012videos_total")
view_like_count_limit = 2000
comment_count_limit = 0
filter_tags = ["climateanxiety", "ecoanxiety"] # Write tags you want it to include ["climateanxiety", "ecoanxiety"], leave [] empty if you do not want to filter per tags


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

# Assuming your original DataFrame is named 'df'
filtered_df = df[(df['view_count'] > view_like_count_limit) | (df['like_count'] > view_like_count_limit)]
filtered_df = filtered_df[filtered_df["comment_count"] > comment_count_limit]
if(len(filter_tags) > 0):
    print("Time to filter by tags")
    # Convert hashtag_names into a list and check if it contains any word from filter_tags
    filtered_df['hashtag_names'] = filtered_df['hashtag_names'].apply(ast.literal_eval)
    filtered_df = filtered_df[filtered_df['hashtag_names'].apply(lambda x: any([k in x for k in filter_tags]))]

filtered_df = filtered_df.sort_values(by='view_count', ascending=False)

# Calculate the average comment_count from the filtered DataFrame
average_comment_count = filtered_df['comment_count'].mean()
# Get the minimum and maximum 'create_time' values
min_create_time = filtered_df['create_time'].min()
max_create_time = filtered_df['create_time'].max()

# Print the date range
print(f"Date Range: {min_create_time} to {max_create_time}, average_comment_count: {average_comment_count}")

# Define the path to the CSV file where you want to save the DataFrame
csv_file_path = Path.cwd() / "data" / f"2020010120231012_{view_like_count_limit}_{comment_count_limit}_{''.join(filter_tags)}.csv"

# Save the DataFrame to the CSV file
filtered_df.to_csv(csv_file_path, index=False)  # Set index=False to exclude the DataFrame's index column

print("Saved filtered data to " + str(csv_file_path))