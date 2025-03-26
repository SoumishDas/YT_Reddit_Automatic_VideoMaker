import google.generativeai as genai

# Set up your API key
genai.configure(api_key="")

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

if __name__ == "__main__":
    text_to_process = "I've rented from the same place for over a year now an it's been good but so far the landlord asks for rent early almost every month.. now he wants me to give it to my roomate to give to him which is ok. My roomate told me at the beginning  of the month an told me 2 days ago, but it was still over a week an said ok just hsve it by next week (the 1st  ) but yesterday  he told me he is seeing him today an wanted it in cash which made me feel weird but I did it. I had the cash but told him I needed more of a heads up . I'm ok but it does change my plans for things an paying for other stuff since my pay day is Friday. I've been late by rent 1 or 2 days but that's it. An always with clear communication.  I dunno I feel angry the more I think of this and I just want to know AITA  for feeling like this. I want to say something  but I'm nervous  an idk if I'm just being an ass.."
    caption, description = generate_caption_and_description(text_to_process)
    
    print("Caption:", caption)
    print("Description:", description)
