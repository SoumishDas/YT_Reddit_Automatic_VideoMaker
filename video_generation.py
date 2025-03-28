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
import json
import whisper

import praw
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    AudioClip,
    concatenate_audioclips,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    ColorClip
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

CHUNK_SIZE = 8  # Number of words per chunk (example)

# (C) Paths/Filenames
BACKGROUND_VIDEOS_FOLDER = "videos"
VIDEO_OUTPUT_FILE = "output_videos/final_output.mp4"

# (D) Whisper model
model = whisper.load_model("medium")








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
# Fetch a Reddit Post
##################################

def fetch_reddit_post(verbose:bool=False) -> str:

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

    subreddit = reddit.subreddit('AmItheAsshole')
    post = next(subreddit.new(limit=1))  # Get the newest post
    text_content = f"{post.title}\n\n{post.selftext}"

    if verbose:
        print("Fetched Post:")
        print(text_content)

    return text_content


##################################
# Generate Audio for Text
##################################

def wav_generation_for_whole_text(text_content:str) -> str:
    
    wav_filename = os.path.join(OUTPUT_DIR, f"audio.wav")
    generate_wav_from_text(text_content, wav_filename)

    clip = AudioFileClip(wav_filename)
    duration = clip.duration
    
    return wav_filename, duration



def word_lvl_transcriptions(audiofile_path:str) -> list:
    result = model.transcribe(audiofile_path,word_timestamps=True)
    
    # each subtitle segment
    # for each in result['segments']:
    #     print (each)

    wordlevel_info = []

    for each in result['segments']:
        words = each['words']
        for word in words:
            # print (word['word'], "  ",word['start']," - ",word['end'])
            wordlevel_info.append({'word':word['word'].strip(),'start':word['start'],'end':word['end']})
    # print(wordlevel_info)

    with open('data.json', 'w') as f:
        json.dump(wordlevel_info, f,indent=4)

    return wordlevel_info
     


def split_text_into_lines(data):

    MaxChars = 80 
    #maxduration in seconds
    MaxDuration = 3.0
    #Split if nothing is spoken (gap) for these many seconds
    MaxGap = 1.5

    subtitles = []
    line = []
    line_duration = 0
    line_chars = 0


    for idx,word_data in enumerate(data):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        line.append(word_data)
        line_duration += end - start
        
        temp = " ".join(item["word"] for item in line)
        

        # Check if adding a new word exceeds the maximum character count or duration
        new_line_chars = len(temp)

        duration_exceeded = line_duration > MaxDuration 
        chars_exceeded = new_line_chars > MaxChars 
        if idx>0:
          gap = word_data['start'] - data[idx-1]['end'] 
          maxgap_exceeded = gap > MaxGap
        else:
          maxgap_exceeded = False
        

        if duration_exceeded or chars_exceeded or maxgap_exceeded:
            if line:
                subtitle_line = {
                    "word": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "textcontents": line
                }
                subtitles.append(subtitle_line)
                line = []
                line_duration = 0
                line_chars = 0


    if line:
        subtitle_line = {
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line
        }
        subtitles.append(subtitle_line)

    
    for line in subtitles:
        json_str = json.dumps(line, indent=4)

    return subtitles, json_str


##################################
# Choose a Background Video
##################################

def choose_bg_vid(total_audio_duration):
    video_files = glob.glob(os.path.join(BACKGROUND_VIDEOS_FOLDER, '*.mp4'))
    if not video_files:
        raise FileNotFoundError(f"No MP4 files found in '{BACKGROUND_VIDEOS_FOLDER}'.")

    bg_video_file = random.choice(video_files)
    print(f"Selected background video: {bg_video_file}")

    background_clip = VideoFileClip(bg_video_file).set_duration(total_audio_duration)

    return background_clip




def create_caption(textJSON, framesize, font = "montserrat-bold",fontsize=60, color='white', bgcolor='blue'):
    wordcount = len(textJSON['textcontents'])
    full_duration = textJSON['end']-textJSON['start']

    word_clips = []
    xy_textclips_positions =[]
    
    x_pos = 0
    y_pos = 0
    # max_height = 0
    frame_width = framesize[0]
    frame_height = framesize[1]
    x_buffer = frame_width*1/5
    y_buffer = frame_height*1/3


    for index, wordJSON in enumerate(textJSON['textcontents']):
      duration = wordJSON['end']-wordJSON['start']
      word_clip = TextClip(wordJSON['word'], font = font, fontsize=fontsize, color=color).set_start(textJSON['start']).set_duration(full_duration)
      word_clip_space = TextClip(" ", font = font,fontsize=fontsize, color=color).set_start(textJSON['start']).set_duration(full_duration)
      word_width, word_height = word_clip.size
      space_width,space_height = word_clip_space.size
      if x_pos + word_width+ space_width > frame_width-2*x_buffer:
            
            # Move to the next line
            x_pos = 0
            y_pos = y_pos + word_height +40

            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos":x_pos+x_buffer,
                "y_pos": y_pos+y_buffer,
                "width" : word_width,
                "height" : word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos+x_buffer, y_pos+y_buffer))
            word_clip_space = word_clip_space.set_position((x_pos+ word_width + x_buffer, y_pos+y_buffer))
            x_pos = word_width + space_width
      else:
            # Store info of each word_clip created
            xy_textclips_positions.append({
                "x_pos":x_pos+x_buffer,
                "y_pos": y_pos+y_buffer,
                "width" : word_width,
                "height" : word_height,
                "word": wordJSON['word'],
                "start": wordJSON['start'],
                "end": wordJSON['end'],
                "duration": duration
            })

            word_clip = word_clip.set_position((x_pos+x_buffer, y_pos+y_buffer))
            word_clip_space = word_clip_space.set_position((x_pos+ word_width+ x_buffer, y_pos+y_buffer))

            x_pos = x_pos + word_width+ space_width


      word_clips.append(word_clip)
      word_clips.append(word_clip_space)  


    for highlight_word in xy_textclips_positions:
      
      word_clip_highlight = TextClip(highlight_word['word'], font = font,fontsize=fontsize, color=color,bg_color = bgcolor).set_start(highlight_word['start']).set_duration(highlight_word['duration'])
      word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
      word_clips.append(word_clip_highlight)

    return word_clips

def gen_vid_beta(audiofilename, linelevel_subtitles, frame_size, duration):
    all_linelevel_splits=[]

    for line in linelevel_subtitles:
        out = create_caption(line,frame_size)
        all_linelevel_splits.extend(out)


    # Load the input video
    input_video = choose_bg_vid(duration).without_audio()
    input_audio = AudioFileClip(audiofilename)

    # Create a color clip with the given frame size, color, and duration
    # background_clip = ColorClip(size=frame_size, color=(0, 0, 0)).set_duration(input_video_duration)

    # If you want to overlay this on the original video uncomment this and also change frame_size, font size and color accordingly.
    final_video = CompositeVideoClip([input_video] + all_linelevel_splits)

    # final_video = CompositeVideoClip(input_video + [background_clip] + all_linelevel_splits)

    final_video = final_video.set_audio(input_audio)

    # Save the final clip as a video file with the audio included
    final_video.write_videofile(VIDEO_OUTPUT_FILE, fps=24)
    print(f"Video created: {VIDEO_OUTPUT_FILE}")


##################################
# 8. Create Text Overlays
##################################

# def create_text_overlays(text_segments, background_clip):

#     text_clips = []
#     for seg in text_segments:
#         txt_clip = TextClip(
#             seg['text'],
#             fontsize=60,         
#             color='white',
#             font='montserrat-bold', 
#             method='caption',
#             size=(int(background_clip.size[0] * 0.6), None),
#             # bg_color='black',
#             stroke_color='black',
#             stroke_width=0,
#             align="center",
#         ).set_start(seg['start']) \
#         .set_duration(seg['duration']) \
#         .set_position('center')
        
#         text_clips.append(txt_clip)

#     return text_clips

# ##################################
# # 9. Composite Final Video
# ##################################

# def compose_final_vid(background_clip, final_audio, text_clips):

#     final_video = CompositeVideoClip([background_clip] + text_clips)
#     final_video = final_video.set_audio(final_audio)
    
#     # 10. Export the Final Video

#     final_video.write_videofile(VIDEO_OUTPUT_FILE, fps=24)
#     print(f"Video created: {VIDEO_OUTPUT_FILE}")


###################################
# MAIN PIPELINE FOR VIDEO CREATION
###################################

def main_video_generation_pipeline() -> str:

    text_content = fetch_reddit_post(verbose=True)
    path, duration = wav_generation_for_whole_text(text_content)
    word_lvl_info = word_lvl_transcriptions(path)
    linelevel_subtitles, jsonStr = split_text_into_lines(word_lvl_info)
    frame_size = (1920, 1080)
    gen_vid_beta(path,linelevel_subtitles,frame_size, duration)

    print("Success :D")
    return text_content



if __name__ == "__main__":
    # main_video_generation_pipeline()
    # text = fetch_reddit_post(verbose=True)
    text = '''I (27M) live with my partner (38M) of five years in central Europe, we are both immigrants. 

We have two children, I will call them A(3F) and B(2F) together. 

My family lives in my homeland so I am here completely alone, due my work and children I don't have any friend here. My partners family (parents, brother and sister) live close to us and he has a lot of friends which I have never met. '''
    path, duration = wav_generation_for_whole_text(text)
    word_lvl_info = word_lvl_transcriptions(path)
    linelevel_subtitles, jsonStr = split_text_into_lines(word_lvl_info)
    frame_size = (1920, 1080)
    gen_vid_beta(path,linelevel_subtitles,frame_size, duration)