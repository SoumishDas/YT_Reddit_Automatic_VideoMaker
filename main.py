import video_generation 
import fetch_title 
import upload_to_yt 

# Generate Video
text_content = video_generation.gen_vid_beta()

# Generate Title and Desc
title, description = fetch_title.generate_caption_and_description(text=text_content)

# Upload to YT
# DOESNT WORK YET/NOT TESTED CLIENT SECRET REQUIRED
response = upload_to_yt.upload_video(file_path="output_videos/final_output.mp4", title=title, description=description,categoryId=24)

print(response)
