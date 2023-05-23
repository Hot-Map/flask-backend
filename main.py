import os
import time
import threading
from datetime import datetime
from video_processor import task
from database import DATABASE, STATUS
from werkzeug.utils import secure_filename
from app import app, set_config, filter_dictionary
from flask import flash, request, redirect, url_for, render_template, jsonify, send_from_directory

SERVER_IS_RUNNING = True
lock = threading.Lock()


@app.route("/")
def upload_form():
    return render_template("upload.html")


@app.route("/", methods=["POST"])
def upload():
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)
    proportion = float(request.form.get("proportion", 0.30))
    audio = int(request.form.get("audio", 1))
    file = request.files["file"]
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)
    else:
        filename = file.filename
        file_extension = os.path.splitext(filename)[-1]
        filename = filename.replace(file_extension, "")

        now = datetime.now()
        save_filename = secure_filename(filename + "_" + str(now) + file_extension)
        file.save(os.path.join(app.config['APP']["UPLOAD_FOLDER"], save_filename))

        uuid = DATABASE.insert_video(
            video_name=filename,
            datetime=now,
            proportion=proportion,
            audio=audio,
            type=file_extension[1:],
            saved_name=save_filename,
            status=STATUS.uploaded,
        )
        print("dd", filename, file_extension)
        return render_template("upload.html", filename=save_filename, video_id=uuid)


@app.route("/upload", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return redirect(request.url)
    proportion = float(request.form.get("proportion", 0.30))
    audio = int(request.form.get("audio", 1))
    
    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)
    else:
        try:
            filename = file.filename
            file_extension = os.path.splitext(filename)[-1]
            filename = filename.replace(file_extension, "")

            now = datetime.now()
            save_filename = secure_filename(filename + "_" + str(now) + file_extension)
            file.save(os.path.join(app.config['APP']["UPLOAD_FOLDER"], save_filename))
            video_id = DATABASE.insert_video(
                video_name=filename,
                datetime=now,
                proportion=proportion,
                audio=audio,
                type=file_extension[1:],
                saved_name=save_filename,
                status=STATUS.uploaded,
            )

            status = DATABASE.get_video_field(video_id=video_id, field="status")
            while status == STATUS.uploaded | status == STATUS.processing:
                time.sleep(3)
        except Exception as e:
            print(e)
            print("Something went wrong")
            jsonify({"error": "Something went wrong"})

        try:
            filename = DATABASE.get_video_field(video_id=video_id, field="summary_name")
            print("filename", filename)
            if filename == "":
                return jsonify({"error": f"{video_id} is not ready"})
            return video_id  # jsonify({'video_id': video_id})
        except Exception as e:
            print(e)
            print(video_id)
            return jsonify({"error": "video_id is not valid"})


@app.route("/display/<filename>")
def display_video(filename):
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


@app.route("/status/<path:video_id>", methods=["GET"])
def get_video(video_id):
    try:
        print("video_id", video_id)
        status = DATABASE.get_video_field(video_id=video_id, field="status")
        print(status)
        if status is None:
            response = {"error": "video_id is not valid"}
        else:
            response = {"status": status}
    except Exception as e:
        response = {"exception": e}

    return jsonify(response)


@app.route("/remove/<path:video_id>", methods=["GET"])
def remove(video_id):
    try:
        status = DATABASE.get_video_field(video_id=video_id, field="status")
        if status == STATUS.processing:
            return video_id + " is under process. Cannot be deleted right now."
        filename = DATABASE.get_video_field(video_id=video_id, field="saved_name")
        summary_filename = DATABASE.get_video_field(video_id=video_id, field="summary_name")
        print("Removing:", filename, ", ", summary_filename)
        if filename is not None:
            try:
                os.remove(os.path.join(app.config['APP']["UPLOAD_FOLDER"], filename))
            except:
                pass
        if summary_filename is not None:
            if summary_filename !='':
                try:
                    os.remove(os.path.join(app.config['APP']["SUMMARY_FOLDER"], summary_filename))
                except:
                    pass
        DATABASE.update_video(video_id=video_id, field="status", value=STATUS.removed)
    except Exception as e:
        pass
    return video_id + " " + "removed"


@app.route("/download/<path:video_id>", methods=["GET"])
def download(video_id):
    try:
        filename = DATABASE.get_video_field(video_id=video_id, field="summary_name")
        print("filename", filename)
        if filename == "":
            return jsonify({"error": f"{video_id} is not ready"})
        return send_from_directory(
            app.config['APP']["SUMMARY_FOLDER"], filename, as_attachment=True
        )
    except Exception as e:
        print(e)
        print(video_id)
        return jsonify({"error": "video_id is not valid"})
    
@app.route("/config/<path:section>", methods=["GET"])
def update_config(section):
    try:
        if section.lower() =='default':
            set_config(app)
            return jsonify(filter_dictionary(app.config))

        section = section.upper()
        if section in app.config.keys():
            if isinstance(app.config[section], dict):
                for k, v in request.args.items():
                    k = k.upper()
                    print(k, v)
                    if k in app.config[section].keys():
                        print(2, k, v)
                        v_type = type(app.config[section][k]) if app.config[section][k] is not None else type("")
                        print(v_type)
                        print(v_type(v))
                        app.config[section][k] = v_type(v)
    except Exception as e:
        print(e)
    return jsonify(filter_dictionary(app.config))

@app.route("/config", methods=["GET"])
def config():
    return jsonify(filter_dictionary(app.config))


def run_script():
    global SERVER_IS_RUNNING
    while SERVER_IS_RUNNING:
        task(app.config)

    print(f"Processing Thread with id {threading.current_thread().ident} closed")


if __name__ == "__main__":
    with lock:
        SERVER_IS_RUNNING = True

    thread = threading.Thread(target=run_script)
    thread.start()

    app.run(host="0.0.0.0", port=5001, debug=True)

    with lock:
        SERVER_IS_RUNNING = False

    thread.join()

    print(f"Server Thread with id {threading.current_thread().ident} closed")
    print("end")
