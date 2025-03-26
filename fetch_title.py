import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables
api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-pro")

def generate_caption_and_description(text):
    prompt = f"Generate a caption and a two liner description for the following text:\n\n{text}\n\nFormat the output as:\nCaption: <caption>\nDescription: <description>"
    
    response = model.generate_content(prompt)
    
    # Extract text response
    result = response.text if response else "No response received."
    
    # Split into caption and description
    lines = result.split("\n")
    caption = next((line.replace("Caption:", "").strip() for line in lines if "Caption:" in line), "No caption found.")
    description = next((line.replace("Description:", "").strip() for line in lines if "Description:" in line), "No description found.")
    
    return caption, description


# TEST JUST IN CASE WE NEED IT LATER

# Test the function
# text = "The quick brown fox jumps over the lazy dog."
# caption, description = generate_caption_and_description(text)
# print("Caption:", caption)
# print("Description:", description)
