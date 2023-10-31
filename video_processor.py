import os
import yt_dlp
from moviepy.editor import VideoFileClip, TextClip, concatenate_videoclips
import openai
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# Initialize OpenAI API
openai.api_key = '<Your OpenAI api>'

def extract_audio_from_video(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
        info = ydl.extract_info(video_url, download=False)
        video_id = info.get("id", None)
        audio_file = f"{video_id}.mp3"
    return audio_file

def generate_video_summary(audio_path):
    with open(audio_path, 'rb') as f:
        response = openai.Completion.create(
            model="text-davinci-002",
            prompt=f"Summarize the following audio content: {f.read()}",
            max_tokens=150
        )
    return response.choices[0].text.strip()

def split_and_subtitles(video_path, transcription):
    video = VideoFileClip(video_path)
    clip_duration = 50
    clips = [video.subclip(i, i+clip_duration) for i in range(0, int(video.duration), clip_duration)]
    
    output_clips = []
    for idx, clip in enumerate(clips):
        txt_clip = TextClip(transcription, fontsize=24, color='white').set_pos('bottom').set_duration(clip.duration)
        video_with_subtitles = concatenate_videoclips([clip, txt_clip.set_start(0).crossfadein(0.5)])
        output_path = f"shorts/clip_{idx}.mp4"
        video_with_subtitles.resize(height=1080).write_videofile(output_path, codec="libx264", audio_codec="aac")
        output_clips.append(output_path)
    return output_clips

def upload_video_to_youtube(filename, title, description, category_id="22"):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "credentials.json"
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, ["https://www.googleapis.com/auth/youtube.upload"])
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
    request_body = {
        "snippet": {
            "categoryId": category_id,
            "description": description,
            "title": title
        },
        "status": {
            "privacyStatus": "private"
        }
    }
    with open(filename, "rb") as video_file:
        response_upload = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=googleapiclient.http.MediaIoBaseUpload(video_file, mimetype="video/mp4")
        ).execute()
    return response_upload

def main():
    video_url = input("Enter the YouTube video URL: ")
    audio_path = extract_audio_from_video(video_url)
    transcription = generate_video_summary(audio_path)
    shorts_clips = split_and_subtitles(video_url, transcription)
    for clip in shorts_clips:
        title = "Short Clip Title"
        description = "Description for the short clip"
        upload_video_to_youtube(clip, title, description)

if __name__ == "__main__":
    main()
