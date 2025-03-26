auth = {
    "client_id":"3latcVZ4rfd6xckc1dUb-w",
    "client_secret":"bNVZTSipGUudAsn7rRIkIgXzN9FzYA",
    "user_agent":"script by u/yourusername",
    "redirect_uri":"http://localhost:8080",
    "refresh_token":"507366339643-9HR-TVngknaPEv820WBGUAX2eyU_lg"
}

import os
import subprocess
import random
import glob
import nltk
from nltk.tokenize import sent_tokenize

import praw
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    concatenate_audioclips,
    TextClip,
    CompositeVideoClip
)

##################################
# 1. Configuration
##################################

# (A) Reddit credentials
REDDIT_CLIENT_ID = '3latcVZ4rfd6xckc1dUb-w'
REDDIT_CLIENT_SECRET = 'bNVZTSipGUudAsn7rRIkIgXzN9FzYA'
REDDIT_USER_AGENT = 'Yt_channel_AITA_Scraper'

# (B) Piper CLI settings
PIPER_MODEL_NAME = "en_US-amy-medium"  # Or full path if needed
OUTPUT_DIR = "audio_sentences"        # Where to store per-sentence WAV files

# (C) Paths/Filenames
BACKGROUND_VIDEOS_FOLDER = "background_videos"
VIDEO_OUTPUT_FILE = "final_output.mp4"

# Download NLTK data for sentence tokenization (only needed once)
nltk.download('punkt')

##################################
# 2. Setup and Functions
##################################

def generate_wav_from_text(text, output_wav):
    """
    Uses Piper via subprocess to generate a WAV for the given text.
    The text is passed via stdin to Piper, which writes to output_wav.
    """
    # We'll use the subprocess.run approach with `input=...` to avoid shell quoting issues
    command = [
        "piper",
        "--model", PIPER_MODEL_NAME,
        "--output_file", output_wav
    ]
    subprocess.run(command, input=text.encode("utf-8"), check=True)

##################################
# 3. Fetch a Reddit Post
##################################

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

subreddit = reddit.subreddit('AmItheAsshole')
post = next(subreddit.new(limit=1))  # Get the newest post
text_content = f"{post.title}\n\n{post.selftext}"

print("Fetched Post:")
print(text_content)

##################################
# 4. Split into Sentences
##################################

sentences = sent_tokenize(text_content)
if not sentences:
    raise ValueError("No sentences found in the post.")

# Create output directory for sentence WAVs
os.makedirs(OUTPUT_DIR, exist_ok=True)

##################################
# 5. Generate WAV for Each Sentence and Collect Durations
##################################

audio_clips = []
sentence_segments = []
current_start = 0.0

for i, sentence in enumerate(sentences, start=1):
    # 1) Generate WAV for this sentence
    wav_filename = os.path.join(OUTPUT_DIR, f"sentence_{i}.wav")
    generate_wav_from_text(sentence, wav_filename)
    
    # 2) Load the WAV to get its duration
    clip = AudioFileClip(wav_filename)
    duration = clip.duration
    
    # 3) Store the audio clip in a list for concatenation later
    audio_clips.append(clip)
    
    # 4) Keep track of start time/duration for text overlay
    sentence_segments.append({
        'text': sentence,
        'start': current_start,
        'duration': duration
    })
    
    # 5) Update the timeline
    current_start += duration

##################################
# 6. Concatenate All Audio Clips
##################################

final_audio = concatenate_audioclips(audio_clips)
total_audio_duration = final_audio.duration
print(f"Total narration length: {total_audio_duration:.2f} seconds")

##################################
# 7. Choose a Background Video
##################################

video_files = glob.glob(os.path.join(BACKGROUND_VIDEOS_FOLDER, '*.mp4'))
if not video_files:
    raise FileNotFoundError(f"No MP4 files found in '{BACKGROUND_VIDEOS_FOLDER}'.")

bg_video_file = random.choice(video_files)
print(f"Selected background video: {bg_video_file}")

background_clip = VideoFileClip(bg_video_file).set_duration(total_audio_duration)

##################################
# 8. Create Text Overlays
##################################

text_clips = []
for seg in sentence_segments:
    txt_clip = TextClip(
        seg['text'],
        fontsize=48,         # Adjust for larger/smaller text
        color='white',
        font='Arial-Bold',   # or another bold font installed on your system
        method='caption',
        # size=background_clip.size,
        # bg_color='black',
        stroke_color='black',
        stroke_width=2
    ).set_start(seg['start']) \
     .set_duration(seg['duration']) \
     .set_position('center')
    
    text_clips.append(txt_clip)

##################################
# 9. Composite Final Video
##################################

final_video = CompositeVideoClip([background_clip] + text_clips)
final_video = final_video.set_audio(final_audio)

##################################
# 10. Export the Final Video
##################################

final_video.write_videofile(VIDEO_OUTPUT_FILE, fps=24)
print(f"Video created: {VIDEO_OUTPUT_FILE}")
