from flask import Flask, request, jsonify, render_template, send_file
import os
import uuid
from SummaryWriter import summarize_text
from generate_docx import create_docx
from TranscriptGenerator import generate_text

# Flask Application
app = Flask(__name__)

# Route to render the HTML template
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and text generation
@app.route('/generate-text', methods=['POST'])
def generate_text_route():
    if 'video' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    video = request.files['video']
    
    if video.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Generate a unique folder name based on the video filename
    video_name = os.path.splitext(video.filename)[0]
    folder_path = os.path.join('uploads', video_name)
    count = 1

    # Ensure the folder name is unique by adding a count suffix if necessary
    while os.path.exists(folder_path):
        folder_path = os.path.join('uploads', f"{video_name}_{count}")
        count += 1

    # Create the unique folder
    os.makedirs(folder_path, exist_ok=True)

    # Save the uploaded video inside the created folder
    video_path = os.path.join(folder_path, video.filename)
    video.save(video_path)

    # Generate text from the video
    Text = generate_text(video_path,folder_path)

    # Summarize the text
    Summary = summarize_text(Text)

    # Create transcript and summary documents with the same base name as the video
    transcript_docx_path = create_docx(Text, folder_path, video_name + "_Transcript")
    summary_docx_path = create_docx(Summary, folder_path, video_name + "_Summary")

    # Return download links for the DOCX files
    return jsonify({
        'transcript': f'/download/{os.path.basename(folder_path)}/{os.path.basename(transcript_docx_path)}',
        'summary': f'/download/{os.path.basename(folder_path)}/{os.path.basename(summary_docx_path)}'
    })

# Route to download files
@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    file_path = os.path.join('uploads', folder, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
