import os
import random
import glob
import nltk
from gtts import gTTS
import praw
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip

# Download NLTK tokenizer data (only needed the first time)
nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize

auth = {
    "client_id":"3latcVZ4rfd6xckc1dUb-w",
    "client_secret":"bNVZTSipGUudAsn7rRIkIgXzN9FzYA",
    "user_agent":"script by u/yourusername",
    "redirect_uri":"http://localhost:8080",
    "refresh_token":"507366339643-9HR-TVngknaPEv820WBGUAX2eyU_lg"
}

### 1. Scrape a Reddit Post Using PRAW ###
# Replace with your own Reddit API credentials
reddit = praw.Reddit(
    client_id=auth.get("client_id"),
    client_secret=auth.get("client_secret"),
    user_agent='Yt_channel_AITA_Scraper',
)

# Choose the subreddit (in this case, "AmItheAsshole") and fetch one post
subreddit = reddit.subreddit('AmItheAsshole')
post = next(subreddit.hot(limit=1))
# Combine title and body text
text_content = f"{post.title}\n\n{post.selftext}"
print("Fetched Post:")
print(text_content)

### 2. Generate Narration Audio with gTTS ###
# We use Google TTS for narration generation
tts = gTTS(text=text_content, lang='en')
audio_file = 'narration.mp3'
tts.save(audio_file)
print(f"Narration saved as {audio_file}")

### 3. Select a Background Video ###
# Assumes you have MP4 files in a folder named 'background_videos'
video_files = glob.glob(os.path.join('background_videos', '*.mp4'))
if not video_files:
    raise Exception("No background videos found in the 'background_videos' folder.")
bg_video_file = random.choice(video_files)
print(f"Selected background video: {bg_video_file}")
background = VideoFileClip(bg_video_file)

### 4. Estimate Timing for Text Segments ###
# Split the full text into sentences
sentences = sent_tokenize(text_content)

# Load the generated narration audio to determine its duration
audio_clip = AudioFileClip(audio_file)
audio_duration = audio_clip.duration

# Calculate total word count to proportionally assign durations
total_words = sum(len(sentence.split()) for sentence in sentences)

# Create timing info for each sentence (naively assigning duration based on word count)
segments = []
current_time = 0.0
for sentence in sentences:
    word_count = len(sentence.split())
    # Proportionally determine the segment duration relative to the full audio length
    segment_duration = (word_count / total_words) * audio_duration
    segments.append({'text': sentence, 'start': current_time, 'duration': segment_duration})
    current_time += segment_duration

### 5. Create Text Overlays Synchronized with the Audio ###
text_clips = []
for segment in segments:
    # Create a text clip for each sentence. Adjust fontsize and method as needed.
    txt_clip = TextClip(
        segment['text'], 
        fontsize=24, 
        color='white', 
        method='caption', 
        size=background.size, 
        align='center'
    )
    # Set when the text appears and how long it stays on screen
    txt_clip = txt_clip.set_start(segment['start']).set_duration(segment['duration']).set_position('center')
    text_clips.append(txt_clip)

### 6. Composite the Final Video ###
# Adjust the background video duration to match the narration audio
video = background.set_duration(audio_duration)
# Combine background and all text clips
final_video = CompositeVideoClip([video] + text_clips)
# Add the narration audio
final_video = final_video.set_audio(audio_clip)

# Output file name
output_file = "final_output.mp4"
final_video.write_videofile(output_file, fps=24)

print(f"Video created successfully: {output_file}")
