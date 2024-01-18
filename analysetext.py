from tiktokfunctions import create_raw_text_data_from_comments, create_raw_data_from_video_descriptions
from pathlib import Path
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import re


wordcloud_figure_name = "wordcloud" # change the name of the resulting .png figure

#output_file = Path.cwd() / "data/comments/rawtextdata.txt"
output_file = create_raw_text_data_from_comments() # comment this line out if you already have a txt file with raw data
#output_file = create_raw_data_from_video_descriptions(Path.cwd() / "data\\2020010120231012filtered_over2000.csv", subtract_hashtags=True) # to use video descriptions

# Check if the folder exists
if not output_file.exists():
    raise FileNotFoundError(f"The file '{output_file}' does not exist.")

# Initialize a list to store the extracted text
extracted_text = []

# Read the text from the file
with open(output_file, "r", encoding="utf-8") as text_file:
    for line in text_file:
        extracted_text.append(line.strip())

# Combine the extracted text into a single string
text = " ".join(extracted_text)
#print("Finished reading text " + text) # comment this when many comments
if text == "":
    raise ValueError("The extracted text from comments is empty, check that the folder exists and contains csv comment files");

text = re.sub(r'\b\w{1,1}\b', '', text) # delete everything that is one letter long

hashtags = ["climateanxiety", "ecoanxiety", "climatedoom", "climatedoomism", "climategrief", "climateoptimism", "ecoguilt", "klimaangst"]
# Define a list of custom stopwords to add
custom_stopwords = ["is", "this", "and", "but", "by", "that", "it'", "will", "going", "that'", 
                    "ve", "ll", "re", "ye", "im", "ga", "es"]

# Get the default set of stopwords from WordCloud
default_stopwords = set(STOPWORDS)

# Extend the default stopwords with custom stopwords
all_stopwords = default_stopwords.union(custom_stopwords)

# Create a WordCloud object
wordcloud = WordCloud(width=800, height=400, background_color="white", stopwords=all_stopwords).generate(text)

# Display the word cloud using matplotlib
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")

# Specify the folder and file path to save the figure
figures_folder = Path.cwd() / "figures"  # Replace with the actual folder path
output_file_path = figures_folder / (wordcloud_figure_name + ".png")

# Create the 'figures' folder if it doesn't exist
figures_folder.mkdir(parents=True, exist_ok=True)

# Save the figure to the specified path
plt.savefig(output_file_path)

plt.show()

