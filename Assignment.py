import streamlit as st
import openai
import os
import moviepy.editor as mp
from google.cloud import speech, texttospeech

# Set up Google Cloud credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'https://internshala.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview'


# OpenAI API Key
openai.api_key = '22ec84421ec24230a3638d1b51e3a7dc'

# Function to transcribe audio using Google Speech-to-Text
def transcribe_audio(audio_file):
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_file.read())
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US"
    )
    response = client.recognize(config=config, audio=audio)
    
    transcription = ""
    for result in response.results:
        transcription += result.alternatives[0].transcript
    return transcription

# Function to correct transcription using GPT-4
def correct_transcription(transcription):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert grammar editor."},
            {"role": "user", "content": f"Please correct the following transcription: {transcription}"}
        ]
    )
    corrected_text = response['choices'][0]['message']['content']
    return corrected_text

# Function to generate AI voice using Google Text-to-Speech
def generate_ai_audio(text):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # Journey voice model
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Standard-C",
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    return response.audio_content

# Function to replace audio in video
def replace_audio_in_video(video_path, new_audio_content):
    video = mp.VideoFileClip(video_path)

    # Save the new audio to a file
    with open("temp_audio.mp3", "wb") as out:
        out.write(new_audio_content)

    # Load the new audio file
    new_audio = mp.AudioFileClip("temp_audio.mp3")

    # Replace the audio in the video
    final_video = video.set_audio(new_audio)
    
    # Save the final video
    final_video.write_videofile("output_video.mp4")

    return "output_video.mp4"

# Streamlit UI
st.title("AI Video Audio Replacement")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    # Extract audio and transcribe it
    st.write("Transcribing audio...")
    transcription = transcribe_audio(uploaded_file)
    st.write(f"Original Transcription: {transcription}")

    # Correct transcription with GPT-4
    st.write("Correcting transcription with GPT-4...")
    corrected_text = correct_transcription(transcription)
    st.write(f"Corrected Transcription: {corrected_text}")

    # Generate new audio using Text-to-Speech
    st.write("Generating AI audio...")
    ai_audio = generate_ai_audio(corrected_text)

    # Replace audio in video
    st.write("Replacing audio in video...")
    output_video_path = replace_audio_in_video(uploaded_file, ai_audio)

    # Provide download link for the final video
    st.video(output_video_path)
    st.success("Video processing complete! Download the output video below.")
    st.download_button("Download Output Video", open(output_video_path, "rb"), file_name="output_video.mp4")
