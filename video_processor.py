import time
from database import DATABASE

def task():
    print("tick")
    video = DATABASE.get_video_to_process()
    if video is not None:
        print(video)
        DATABASE.update_video_status(video['id'], "PROCESSING")
        time.sleep(30)
        DATABASE.update_video_status(video['id'], "COMPLETED")
    else:
        time.sleep(30)

