from flask import Flask, request, jsonify, send_file
import os
from Processing import Process
import Config
from werkzeug.utils import secure_filename
from flask_cors import CORS


app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])


UPLOAD_FOLDER = os.path.join(Config.ROOT_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
count = 0
pro = Process()

@app.route('/generate_highlight', methods=['POST'])
def generate_highlight():
    global count
    folders = [name for name in os.listdir(Config.ROOT_DIR) if os.path.isdir(os.path.join(Config.ROOT_DIR, name))]
    count = len(folders) + 1
  
    if 'video' not in request.files:
        return jsonify({'error': 'No video file part in the request'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the uploaded video
    filename = secure_filename(video_file.filename)
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    video_file.save(video_path)

    print(f"Received and saved video: {video_path}")

    # Call your existing processing logic
    output_folder = f"output{count}"
    timestamps_effnet, timestamps_ocr = pro.process_video(video_path)
    # timestamps_effnet = [
    # "00:00:47",
    # "00:01:37",
    # "00:02:10",
    # "00:04:02",
    # "00:04:20",
    # "00:04:57",
    # "00:06:16"
    # ]

    # timestamps_ocr = [
    # (131, 6, (131, 6), "00:01:03"),
    # (132, 7, (132, 7), "00:02:32"),
    # (134, 8, (134, 8), "00:05:01")
    # ]


    new_list = pro.find_closest_timestamps(timestamps_ocr, timestamps_effnet)
    new_list = [(pro.add_seconds_to_time(start, -3), pro.add_seconds_to_time(end, 5)) for start, end in new_list]

    pro.extract_clips_with_ffmpeg(video_path, new_list, output_folder)

    output_filename = f"final_highlighs_video{count}.mp4"
    output_path = os.path.join(Config.ROOT_DIR, output_folder, output_filename)
    pro.concatenate_clips(output_folder, output_path)

    count += 1

    return jsonify({'video_path': f"/get_highlight/{output_folder}/{output_filename}"})

@app.route('/get_highlight/<folder>/<filename>', methods=['GET'])
def get_highlight(folder, filename):
    full_path = os.path.join(Config.ROOT_DIR, folder, filename)
    if os.path.exists(full_path):
        return send_file(full_path, as_attachment=False)
    return jsonify({'error': 'Video not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
