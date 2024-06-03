from django.shortcuts import render
from my_app.models import *
from django.http import HttpResponse
#from django.conf import settings

# video to text
from pytube import YouTube
# from media.videos import *
# new changes
import assemblyai as aai
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt", src_lang = 'en_XX')
import os
#import re

# text->translation->audio
from gtts import gTTS
import threading
from gradio_client import Client
# audio->Video
# import ffmpeg
# ORIGINAL
# regular expressions
import re
import subprocess

# # import pyrebase
# from django.core.files.storage import default_storage
    

# FireBase
# config={
#     "apiKey": "AIzaSyCiH7ajLmGES6v_fDxf43znmUxxTytRYWQ",
#     "authDomain": "translatevoiceindia-5e09b.firebaseapp.com",
#     "projectId": "translatevoiceindia-5e09b",
#     "storageBucket": "translatevoiceindia-5e09b.appspot.com",
#     "messagingSenderId": "243355522097",
#     "appId": "1:243355522097:web:3e5b49258221073724f110",
#     "measurementId": "G-8XKPLQDB5Q",
#     "databaseURL":""
# }

# firebase=pyrebase.initialize_app(config)
# storage=firebase.storage()



# Create your views here.
def home(request):
    # api key
    aai.settings.api_key = "ed93af1011494e71857f9471aa1d7e40"
    transcriber = aai.Transcriber()
    # Create a client object
    client = Client("https://santhosh-madlad400-3b-ct2.hf.space/--replicas/bt2t8/")
    if request.method == 'POST':
        # Check if a video file was uploaded
        language=request.POST['language']
        if 'video_file' in request.FILES:
            video_file = request.FILES['video_file']
            v=Video.objects.create(
                video_file=video_file,
            )
            # saving the video
            v.save()

            #file_save = default_storage.save(video_file.name, video_file)
            #storage.child("files/" + video_file.name).put("media/" + video_file.name)
            #delete = default_storage.delete(video_file.name)
            print("Succeess")
            video_name=video_file.name
            transcript = transcriber.transcribe(f"media/videos/{video_name}")
            engg = transcript.text
            # tokenizer.src_lang = "en_XX"
            # encoded_hi = tokenizer(engg, return_tensors="pt")
            # generated_tokens = model.generate(
            #     **encoded_hi,
            #     forced_bos_token_id=tokenizer.lang_code_to_id["hi_IN"]
            # )
            # tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
            myobj=gTTS(text=engg,lang=language,slow=False)
            myobj.save("media/speech.mp3")
            print("I guess working!")
            return HttpResponse('Video file uploaded successfully!')

        # Check if a video URL was provided
        elif 'video_url' in request.POST:
          print("Entered")
          video_url = request.POST['video_url']
          v=Video.objects.create(
              video_url=video_url
          )
          v.save()
          print("Video Saved!")
          # file_save = default_storage.save(video_file.name, video_file)
          # storage.child("files/" + video_file.name).put("media/" + video_file.name)
          # delete = default_storage.delete(video_file.name)
          # jo aajkal youtube video links provide karta h vo shortened hote h vo pytube support ni karta isliye full_url me convert kra
          shortened_url=v.video_url
          video_id = re.search(r'(?<=be/)[\w-]+', shortened_url).group(0)
          full_url = f"https://www.youtube.com/watch?v={video_id}"
          video_path = '/media/videos'
          try:
            print("TRy Block")
            yt = YouTube(full_url)
            print("hiiii......")
            stream = yt.streams.get_highest_resolution()
            print("hiiii2......")
            v_path=stream.download(video_path)
            print("hiiii3......")
            video_name = os.path.basename(v_path)
            print("hiiii4......")
            print(video_name)
            print("hiiii5......")
            transcript = transcriber.transcribe(f"media/videos/{video_name}")
            engg = transcript.text
            print(engg)
            print("diyaa...............")
            output = chunks(engg)
            print(output)
            print(output[0])
            # Create a list of input texts and target languages
            # input_texts = output
            lock = threading.Lock()
            threads = []
            final_out = []
            i = 0
            # Start the threads
            for i in range(len(output)):
              print(i)
              thread = threading.Thread(target=run_api_call, args=(client, output[i],final_out,language, lock))
              threads.append(thread)
              thread.start()
            # Wait for the threads to finish
            for thread in threads:
              thread.join()

            print(final_out)
            my_string = ''.join(final_out)
            myobj=gTTS(text=my_string,lang=language,slow=False)
            result_string = re.sub('.mp4', "", f'{video_name}')
            myobj.save(f"media/{result_string}_speech.mp3")
            # changes
            # Paths to your video and audio files
            # Paths to your video and audio files
            video_path = f"media/videos/{video_name}"
            audio_path = f"media/{result_string}_speech.mp3"
            print("Video Path:", video_path)
            print("Audio Path:", audio_path)
            # Output file path
            # output_video_path = os.path.join(settings.BASE_DIR, 'media', 'output_synced.mp4')
            # print(output_video_path
            # # ffmpeg command
            # ffmpeg_command = [
            #   "ffmpeg",
            #   "-i", video_path,
            #   "-i", audio_path,
            #   "-c:v", "copy",
            #   "-c:a", "aac",
            #   "-strict", "experimental",
            #   "-map", "0:v:0",
            #   "-map", "1:a:0",
            #   output_video_path
            #     ] 
            # try:
            #   subprocess.run(ffmpeg_command, check=True)
            #   print("I guess working!")
            #   return HttpResponse("Video processed successfully!")
            # except subprocess.CalledProcessError as e:
            #   return HttpResponse(f"Error processing video: {e}")
          except PermissionError:
              print("Permission denied. Check if you have write permissions for:", video_path)
          except Exception as e:
              print("An error occurred:", e)
          return HttpResponse('Video URL submitted successfully!')

    # If the request method is GET or if the form was not submitted
    return render(request,"index.html")

def chunks(text):
  paragraphs = text.split('\n')

  sentences = []
  for paragraph in paragraphs:
    sentences.extend(paragraph.split('.'))

  output = []
  for i in range(0, len(sentences), 3):
    output.append('. '.join(sentences[i:i+3]))

  print('\n'.join(output))
  return output

def run_api_call(client, input_text,final_out,language, lock):
  result = client.predict(
    input_text,
    language,
    api_name="/predict"
  )
  print(result)
  with lock:
    final_out.append(result)
  # final_out.append(result)
  # return final_out








'''

<script type="module">
  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-analytics.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
  const firebaseConfig = {
    apiKey: "AIzaSyCiH7ajLmGES6v_fDxf43znmUxxTytRYWQ",
    authDomain: "translatevoiceindia-5e09b.firebaseapp.com",
    projectId: "translatevoiceindia-5e09b",
    storageBucket: "translatevoiceindia-5e09b.appspot.com",
    messagingSenderId: "243355522097",
    appId: "1:243355522097:web:3e5b49258221073724f110",
    measurementId: "G-8XKPLQDB5Q"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);
</script>


'''