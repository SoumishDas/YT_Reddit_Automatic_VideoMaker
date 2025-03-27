from video_generation import main_vid_generation_pipeline
from fetch_title import generate_caption_and_description
from upload_to_yt import upload_video

# Generate Video
text_content = main_vid_generation_pipeline()

# Generate Title and Desc
title, description = generate_caption_and_description(text=text_content)

# Upload to YT
# DOESNT WORK YET/NOT TESTED CLIENT SECRET REQUIRED
response = upload_video(file_path="output_videos/final_output.mp4", title=title, description=description)

print(response)
