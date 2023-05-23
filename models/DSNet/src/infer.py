import os
import cv2
import numpy as np
import torch
import random
import torchaudio
from moviepy.editor import *

from helpers import init_helper, vsumm_helper, bbox_helper, video_helper
from modules.model_zoo import get_model

def repeat_items(lst, n):
    repeated_list = [item for item in lst for _ in range(n)]
    return np.array(repeated_list)


def main():
    args = init_helper.get_arguments()
    print("args:", args)

    file_name = os.path.splitext(os.path.basename(args.source))[0]

    temp_summary_dir = f"{args.temp_folder}{file_name}.mp4" if args.audio == 'True' else args.save_path
    audio_dir = f"{args.temp_folder}{file_name}.mp3"
    audio_processed_dir = f"{args.temp_folder}{file_name}_processed.mp3"

    if args.audio == 'True':
        print('Exporting audio ...')
        video = VideoFileClip(args.source)
        video.audio.write_audiofile(audio_dir)
        data_waveform, rate_of_sample = torchaudio.load(audio_dir, format="mp3")

    cap = cv2.VideoCapture(args.source)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_summary_dir, fourcc, fps, (width, height))

    frame_labels = []

    if args.development == 'True': #random selected frames
        print('Processing source video ...')
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            take = bool(random.randint(0, 1))
            frame_labels.append(take)
            if take:
                out.write(frame)
            frame_idx += 1
        out.release()
        cap.release()
    
    else:
        # load model
        print('Loading DSNet model ...')
        model = get_model(args.model, **vars(args))
        model = model.eval().to(args.device)
        state_dict = torch.load(args.ckpt_path,
                                map_location=lambda storage, loc: storage)
        model.load_state_dict(state_dict)

        # load video
        print('Preprocessing source video ...')
        video_proc = video_helper.VideoPreprocessor(args.sample_rate, args.device)
        n_frames, seq, cps, nfps, picks = video_proc.run(args.source, args.change_points)
        seq_len = len(seq)

        print('Predicting summary ...')
        with torch.no_grad():
            seq_torch = torch.from_numpy(seq).unsqueeze(0).to(args.device)

            pred_cls, pred_bboxes = model.predict(seq_torch)

            pred_bboxes = np.clip(pred_bboxes, 0, seq_len).round().astype(np.int32)

            pred_cls, pred_bboxes = bbox_helper.nms(pred_cls, pred_bboxes, args.nms_thresh)
            pred_summ = vsumm_helper.bbox2summary(
                seq_len, pred_cls, pred_bboxes, cps, n_frames, nfps, picks)

        print('Writing summary video ...')
        frame_labels = pred_summ
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if pred_summ[frame_idx]:
                out.write(frame)

            frame_idx += 1

        out.release()
        cap.release()

    if args.audio == 'True':
        #print('Processing audio ...')
        audio_labels = repeat_items(frame_labels, int(rate_of_sample/fps))
        #print("frame_labels", len(frame_labels))
        #print("rate_of_sample", rate_of_sample)
        #print("fps", fps)
        #print("rate_of_sample/fps", rate_of_sample/fps)
        #print("int(rate_of_sample/fps)", int(rate_of_sample/fps))
        #print("audio_labels", len(audio_labels))
        ch_list = []
        for ch in data_waveform:
            #print("ch", len(ch))
            ss = min(len(audio_labels), len(ch))
            t_ch = ch[:ss]
            labels = audio_labels[:ss]
            ch_list.append(t_ch[labels==1].numpy())

        new_waveform = torch.Tensor(ch_list)
        torchaudio.save(audio_processed_dir, new_waveform, rate_of_sample)

        video = VideoFileClip(temp_summary_dir)
        audio = AudioFileClip(audio_processed_dir)
        video = video.set_audio(audio)
        video.write_videofile(args.save_path, codec="libx264", audio_codec="aac")

        # Remove temp files
        os.remove(temp_summary_dir)
        os.remove(audio_dir)
        os.remove(audio_processed_dir)


if __name__ == '__main__':
    main()
