import os
import re
import subprocess
from collections import deque, Counter
from datetime import datetime, timedelta
import Config
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
import cv2
from PIL import Image
import easyocr
import warnings
warnings.filterwarnings("ignore")



class Process():

    CNN_model = None
    model_path = os.path.join(Config.ROOT_DIR, "Model Wieghts" , "best_model (1).pth")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    def __init__(self):
        self.set_up_model()
    transform = None

    def set_up_model(self):
        self.CNN_model = models.efficientnet_b0(pretrained=False)
        self.CNN_model.features[0] = nn.Conv2d(1, 32, kernel_size=(3, 3), stride=(2, 2), padding=(1, 1))
        self.CNN_model.classifier[1] = nn.Linear(self.CNN_model.classifier[1].in_features, 2)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.CNN_model = self.CNN_model.to(device)
        self.CNN_model.load_state_dict(torch.load(self.model_path, map_location=device))
        self.CNN_model.eval()

        self.transform = transforms.Compose([
            transforms.Grayscale(num_output_channels=1),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])


    def extract_cricket_score_from_frame(self,frame, reader):
        height, width = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        y_start = int(0.76 * height)
        y_end = int(0.986 * height)
        x_start = 0
        x_end = int(0.47 * width)
        region = gray[y_start:y_end, x_start:x_end]
        _, binary = cv2.threshold(region, 150, 255, cv2.THRESH_BINARY_INV)
        result = reader.readtext(binary, detail=0)
        ocr_text = ' '.join(result)
        match = re.search(r'\b(\d+)-(\d+)\b', ocr_text)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None


    def has_consecutive_repeats(self,seq, value, min_repeat):
        repeat = 0
        for item in seq:
            if item == value:
                repeat += 1
                if repeat >= min_repeat:
                    return True
            else:
                repeat = 0
        return False


    def get_stable_score(self,score_window):
        counts = Counter(score_window)
        for score, count in counts.items():
            if count >= 3:
                if self.has_consecutive_repeats(score_window, score, min_repeat=3) or count == max(counts.values()):
                    return score
        return None


    def process_video(self ,video_path, frame_skip=10):
        print('Model Running')
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        reader = easyocr.Reader(['en'])

        frame_count = 0
        timestamps_effnet = []
        timestamps_ocr = []
        frame_window = []
        pause_counter = 0
        last_score = None
        ocr_score_window = deque(maxlen=15)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if pause_counter > 0:
                pause_counter -= 1
                frame_count += 1
                continue

            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.CNN_model(img_tensor)
                _, predicted = torch.max(outputs, 1)
                prediction = predicted.item()

            frame_window.append(prediction)
            if len(frame_window) > 20:
                frame_window.pop(0)

            if frame_window.count(1) >= 15:
                consecutive_count = 0
                for pred in frame_window:
                    if pred == 1:
                        consecutive_count += 1
                        if consecutive_count >= 9:
                            timestamp_sec = frame_count / fps
                            minutes = int(timestamp_sec // 60)
                            seconds = int(timestamp_sec % 60)
                            hours = int(minutes // 60)
                            minutes = minutes % 60
                            timestamp = f"{hours:02}:{minutes:02}:{seconds:02}"
                            timestamps_effnet.append(timestamp)
                            pause_counter = int(10 * fps)
                            frame_window.clear()
                            break
                    else:
                        consecutive_count = 0

            if frame_count % frame_skip == 0:
                runs, wickets = self.extract_cricket_score_from_frame(frame, reader)
                if runs is not None and wickets is not None:
                    ocr_score_window.append((runs, wickets))

                stable_score = self.get_stable_score(list(ocr_score_window))
                if stable_score:
                    confirmed_runs, confirmed_wickets = stable_score
                    if last_score is None:
                        last_score = (confirmed_runs, confirmed_wickets)
                        should_add = False
                    else:
                        run_diff = confirmed_runs - last_score[0]
                        wicket_diff = confirmed_wickets - last_score[1]
                        valid_run = run_diff in [4, 6]
                        valid_wicket = wicket_diff == 1
                        should_add = valid_run or valid_wicket
                        last_score = (confirmed_runs, confirmed_wickets)
        
                    if should_add:
                        timestamp_sec = frame_count / fps
                        minutes = int(timestamp_sec // 60)
                        seconds = int(timestamp_sec % 60)
                        hours = int(minutes // 60)
                        minutes = minutes % 60
                        timestamp = f"{hours:02}:{minutes:02}:{seconds:02}"
                        timestamps_ocr.append((confirmed_runs, confirmed_wickets, last_score, timestamp))

            frame_count += 1

        cap.release()
        return timestamps_effnet, timestamps_ocr



    def find_closest_timestamps(self ,ocr_list, effnet_list):

        # Convert EfficientNet timestamps to datetime objects for easy comparison
        effnet_times = [datetime.strptime(ts, "%H:%M:%S") for ts in effnet_list]

        # Result list to store combined values
        result = []

        # Loop through each value in the OCR list
        for runs, wickets,_, ocr_timestamp in ocr_list:
            ocr_time = datetime.strptime(ocr_timestamp, "%H:%M:%S")
        
            # Filter only those EfficientNet times that are <= OCR time
            valid_effnet_times = [eff_time for eff_time in effnet_times if eff_time <= ocr_time]
        
            if not valid_effnet_times:
                continue  # skip if no valid timestamp before OCR time
        
            # Now get the closest from valid ones (latest before OCR)
            closest_effnet_time = max(valid_effnet_times, key=lambda eff_time: eff_time)
        
            closest_effnet_str = closest_effnet_time.strftime("%H:%M:%S")
            result.append((closest_effnet_str, ocr_timestamp))


        return result


    def add_seconds_to_time(self ,time_str, seconds_to_add):
        # Convert the time string to a datetime object
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        
        # Add the specified seconds using timedelta
        new_time_obj = time_obj + timedelta(seconds=seconds_to_add)
        
        # Convert it back to a time string
        return new_time_obj.strftime('%H:%M:%S')




    def extract_clips_with_ffmpeg(self,video_path, clip_timestamps,output_folder):

        print("Extracting Clips")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for idx, (start, end) in enumerate(clip_timestamps):
            # Create output file name
            output_file = os.path.join(output_folder, f"clip{idx + 1}.mp4")
            
            # Prepare ffmpeg command
            cmd = [
                'ffmpeg', 
                '-i', video_path, 
                '-ss', start,  # Start time
                '-to', end,    # End time
                '-c', 'copy',  # Copy video codec
                output_file    # Output file path
            ]
            
            # Run the command
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print(f"Extracted clip {idx + 1}: {start} to {end}")


    # def concatenate_clips(self, clip_folder, output_file_name):
        
    #     # Get the full output path using Config.ROOT_DIR
    #     output_path = os.path.join(Config.ROOT_DIR, clip_folder, output_file_name)

    #     # Ensure the clip folder exists
    #     full_clip_folder = os.path.join(Config.ROOT_DIR, clip_folder)
    #     clips = [os.path.join(full_clip_folder, f) for f in os.listdir(full_clip_folder) if f.endswith('.mp4')]
    #     clips.sort()

    #     file_list_path = os.path.join(full_clip_folder, 'clip_list.txt')
    #     with open(file_list_path, 'w') as f:
    #         for clip in clips:
    #             f.write(f"file '{clip}'\n")

    #     cmd = [
    #         'ffmpeg',
    #         '-f', 'concat',
    #         '-safe', '0',
    #         '-i', file_list_path,
    #         '-c', 'copy',
    #         output_path
    #     ]
    #     subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     print(f"Concatenated video saved to {output_path}")



    def natural_sort_key(self , filename):
        """Sort helper that extracts numbers from filenames for natural sort"""
        return [int(text) if text.isdigit() else text.lower() 
                for text in re.split(r'(\d+)', filename)]

    def concatenate_clips(self, clip_folder, output_file_name):
        print('Concatenate Clips')
        # Get the full output path using Config.ROOT_DIR
        output_path = os.path.join(Config.ROOT_DIR, clip_folder, output_file_name)

        # Ensure the clip folder exists
        full_clip_folder = os.path.join(Config.ROOT_DIR, clip_folder)
        clips = [os.path.join(full_clip_folder, f) for f in os.listdir(full_clip_folder) if f.endswith('.mp4')]
        clips.sort(key=self.natural_sort_key)

        # Prepare file list for FFmpeg
        file_list_path = os.path.join(clip_folder, 'clip_list.txt')
        with open(file_list_path, 'w') as f:
            for clip in clips:
                full_path = os.path.join(clip_folder, clip)
                f.write(f"file '{full_path}'\n")

        # FFmpeg command to concatenate with re-encoding (for smooth transitions)
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', file_list_path,
            '-vf', 'scale=1280:720',        # Optional: scale all to 720p
            '-preset', 'fast',
            '-crf', '23',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-movflags', '+faststart',
            output_path
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Concatenated video saved to: {output_path}")

