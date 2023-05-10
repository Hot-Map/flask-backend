import time
import subprocess
from database import DATABASE

def task(config):
    print("tick")
    chck_pt = config['CHECKPOINT']
    video = DATABASE.get_video_to_process()
    if video is not None:
        video_path = config['UPLOAD_FOLDER'] + video['saved_name']
        output_dir = config['SUMMARY_FOLDER'] + 'summary' + video['saved_name']

        command = ["python", "models/DSNet/src/infer.py", "anchor-based", "--ckpt-path", chck_pt, "--source", video_path, "--save-path", output_dir]
        print(command)
        DATABASE.update_video(video['id'], "status", "PROCESSING")
        result = subprocess.run(command, stdout=subprocess.PIPE)
        if result.stdout:
            print(result.stdout)
        if result.returncode == 0:
            print("The subprocess completed successfully!")
            DATABASE.update_video(video['id'], "summary_name", 'summary-' + video['saved_name'])
            DATABASE.update_video(video['id'], "status", "COMPLETED")
        else:
            print("There was an error running the subprocess.")
            DATABASE.update_video(video['id'], "status", "ERROR")
        
    else:
        time.sleep(30)

