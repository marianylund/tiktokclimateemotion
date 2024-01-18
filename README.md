# TikTok Climate Emotions

Scripts used to gather data for a research project led by Martin Venn and Christian Haugestad at University of Oslo, Department of Psychology.

## Generate and add authorization key

Generate the key following TikTok tutorial: https://developers.tiktok.com/doc/client-access-token-management. Then create a `.env` file and add authorization key to it by writing `TIKTOK_KEY = "clt.example12345Example12345Example"`.
(!!!) Access tokens are set to expire every two hours, so you would need to regenerate it.

## Run the code

To run the code, first you need to get it:

### Locally zipped

To run the code, you can download it by clicking "Code" -> "Local" -> "Download ZIP" and unzip it.

<img src="img/image.png" height="400">

Then run `pip install -r requirements.txt` in the terminal in the same folder where `requirements.txt` file is. You have to have Python installed version Python 3.10.8. Every time there is an update on GitHub, you will need to download it again. Then proceed to the next sections.

### In the cloud using Codespaces

Press "Code" -> "Codespaces" -> either create your own or if you can open the "cuddly tribble" (I´m not sure if it is visible to everyone)

<img src="img/codespace.png" height="400">

There open Terminal in the menu where you can run the commands and open files to edit. OBS! Your edits are not automatically shared with others unless you specifically say so, see next section.

<img src="img/codespaceterminalopen.png" height="400">

### Running locally

https://docs.github.com/en/get-started/quickstart/hello-world

## Working functionality

Now you can get the videos by hashtag and get it saved to a .xlsl file and get comments for those videos.

### Get videos

Using official tiktok api, so it needs access token, remember to add it to `.env` file. Then the file will use the key in all other functions.

The script divides the given start and end dates into 30 days chunks (because it is the max given by TikTok API) and goes through them all, merges into the save .csv file and saves it to data folder
Run `python getvideos.py` in the terminal in the same folder as the file.

Creates file with id,create_time,video_description,hashtag_names,comment_count,like_count,view_count,share_count, region_code and link parameters.

Should run `add_index_to_data()` when all videos are downloaded to create an index, it also removes the usernames from descriptions

### Filter videos

Run `python filtervideos.py` in the terminal in the same folder as the file. Remember to give the path to the folder with the data for videos. Pro tip: right click on file and copy full path to paste into the `filtervideos.py` file.
Extracts videos that have more views or likes than a given limit, sorts after view_count and saves to a new csv file in data folder.

### Get comments from videos

Requires a .csv file that you get from `getvideos.py` file. Add the path to the file with the videos to the parameters in `getcommentsfromvideos.py` file. Creates .csv file for each video and adds to `comments` folder.
Run `python getcommentsfromvideos.py` in the terminal in the same folder as the file.
OBS! Creates as many new files as the number of videos, so might take some time. Remember, you can cancel the operation in the terminal by pressing `ctrl + C` or `ctrl + Z`.

According to TikTok API only the top 1000 comments will be returned, so cursor + max_count <= 1000.

Saves raw comments with video_id as its filename just to keep correct track of everything.

### Copy comments

If you have changed the file with videos and want to filter out and only have the comments for the videos left, you can use `copycomments.py`, remember to change the path to the .csv file with videos, source folder where comments are, currently they are in `data/comments` and add a path to folder where filtered comments will be copied to.

When comments are copied, the filename is the same as index of the video, not id.

### Analyse text

Can take in any .txt file, at the start you can define a path to a txt file or generate one from comments folder or video file with descriptions.
Requires `comments` folder with .csv comment files you get from `getcommentsfromvideos.py`.

Run `analysetext.py` in the terminal and it will create a `rawtextdata.txt` file in `comments` folder with just the comments and create a wordcloud figure and save it to `figures` folder.
In `analysetext.py` file you can change the name of figure it creates and comment out (by writing a `#` symbol before that line) creation of `rawtextdata.txt` file if you already have one.

## File explanations (for curious ones, feel free to ignore)

There are some other files you might be curious what they mean:

requirements.txt -> defines external libraries one needs to have installed to run the code, it should ideally run automatically in github codespace, but if you get errors that you are missing some libraries, you can try to run `pip install -r requirements.txt` in the terminal in the same folder where `requirements.txt` file is.

LICENSE -> is created automatically when I copied the project, it is more relevant for if this project is ever public, tells others if they can use the code or not. Since we added a tiktok code, we should not make this project private until we have disabled and deleted the code.

.gitignore -> tells Git what files it should ignore and not sync, so it will not sync any files that end .json, .xlsx or .csv

tiktokfunctions.py -> contains helpful functions
