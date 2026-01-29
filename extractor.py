# extractor.py
import cv2
import os

class VideoExtractor:
    def __init__(self, path):
        self.path = path
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps

    def get_frame_by_time(self, seconds):
        frame_id = int(seconds * self.fps)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def extract_range(
        self,
        start_sec,
        end_sec,
        output_dir,
        prefix="frame_",
        start_index=1,
        save=True,
        progress_callback=None   # 👈 NUEVO
    ):
        start_frame = int(start_sec * self.fps)
        end_frame = int(end_sec * self.fps)

        total = max(end_frame - start_frame, 1)

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        index = start_index

        for i in range(total):
            ret, frame = self.cap.read()
            if not ret:
                break

            if save:
                filename = f"{prefix}{index:05d}.png"
                cv2.imwrite(
                    os.path.join(output_dir, filename),
                    frame
                )
                index += 1

            # 📊 progreso
            if progress_callback:
                progress_callback((i + 1) / total)
