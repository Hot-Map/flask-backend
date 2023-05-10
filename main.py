import os
import threading
import subprocess
from app import app
from datetime import datetime
from database import DATABASE
from werkzeug.utils import secure_filename
from flask import flash, request, redirect, url_for, render_template, jsonify, send_from_directory
from video_processor import task

SERVER_IS_RUNNING = True
lock = threading.Lock()


@app.route('/')
def upload_form():
	return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	else:
		filename = file.filename
		file_extension = os.path.splitext(filename)[-1]
		filename = filename.replace(file_extension, "")

		now = datetime.now()
		save_filename = secure_filename(filename + '_' + str(now) + file_extension)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_filename))
		# print('upload_video filename: ' + filename)
		uuid = DATABASE.insert_video(video_name=filename, datetime=now,
		                             type=file_extension[1:], saved_name=save_filename, status='UPLOADED')
		flash('Video successfully uploaded and displayed below')
		print("dd", filename, file_extension)
		return render_template('upload.html', filename=save_filename)


@app.route('/upload', methods=['POST'])
def upload_video():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	else:
		filename = file.filename
		file_extension = os.path.splitext(filename)[-1]
		filename = filename.replace(file_extension, "")

		now = datetime.now()
		save_filename = secure_filename(filename + '_' + str(now) + file_extension)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_filename))
		# print('upload_video filename: ' + filename)
		uuid = DATABASE.insert_video(video_name=filename, datetime=now,
		                             type=file_extension[1:], saved_name=save_filename, status='UPLOADED')
		flash('Video successfully uploaded and displayed below')
		print("dd", filename, file_extension)
		return jsonify({'video_id': uuid})


@app.route('/display/<filename>')
def display_video(filename):
	return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/api/status', methods=['GET'])
def get_video():
	try:
		video_id = request.args['video_id']
		print("video_id", video_id)
		status = DATABASE.get_video_field(video_id=video_id, field="status")
		print(status)
		if status is None:
			response = {'error': 'video_id is not valid'}
		else:
			response = {'status': status}
	except Exception as e:
		response = {'exception': e}

	return jsonify(response)


@app.route('/download/<path:video_id>', methods=['GET'])
def download(video_id):
	try:
		filename = DATABASE.get_video_field(video_id=video_id, field="summary_name")
		print("filename", filename)
		if filename == "":
			return jsonify({'error': f'{video_id} is not ready'})
		return send_from_directory(app.config['SUMMARY_FOLDER'], filename, as_attachment=True)
	except Exception as e:
		print(e)
		print(video_id)
		return jsonify({'error': 'video_id is not valid'})


@app.route('/download')
def download_video():
    filename = request.args.get('filename')
    print(filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


def run_script():
    global SERVER_IS_RUNNING
    while SERVER_IS_RUNNING: task(app.config)
    print(f"Processing Thread with id {threading.current_thread().ident} closed")
    #subprocess.call(["python", "video_processor.py"])


if __name__ == "__main__":
    with lock: SERVER_IS_RUNNING = True
    thread = threading.Thread(target=run_script)
    thread.start()
    app.run(host="0.0.0.0", port=5001, debug=True)
    with lock: SERVER_IS_RUNNING = False
    thread.join()
    print(f"Server Thread with id {threading.current_thread().ident} closed")
    print("end")