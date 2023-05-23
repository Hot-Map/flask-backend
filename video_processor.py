import time
import torch
import subprocess
from database import DATABASE, STATUS

def task(config):
    print("tick")
    chck_pt = config['MODEL']['CHECKPOINT']
    video = DATABASE.get_video_to_process()
    if video is not None:
        print(video)
        video_path = config['APP']['UPLOAD_FOLDER'] + video['saved_name']
        output_dir = config['APP']['SUMMARY_FOLDER'] + 'summary-' + video['saved_name']
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

        command = ["python", "models/DSNet/src/infer.py", "anchor-based",
                    "--ckpt-path", chck_pt,
                    "--source", video_path,
                    "--save-path", output_dir,
                    "--temp-folder", config['APP']['PROCESS_FOLDER'],
                    "--development", config['APP']['DEVELOPMENT'],
                    "--audio", config['APP']['AUDIO'],
                    "--change-points", config['MODEL']['CHANGE_POINTS'],
                    "--device", device]
        print(command)
        DATABASE.update_video(video['id'], "status", STATUS.processing)
        result = subprocess.run(command, stdout=subprocess.PIPE)
        if result.stdout:
            print(result.stdout)
        if result.returncode == 0:
            print("The subprocess completed successfully!")
            DATABASE.update_video(video['id'], "summary_name", 'summary-' + video['saved_name'])
            DATABASE.update_video(video['id'], "status", STATUS.completed)
        else:
            print("There was an error running the subprocess.")
            DATABASE.update_video(video['id'], "status", STATUS.error)
        
    else:
        time.sleep(30)

