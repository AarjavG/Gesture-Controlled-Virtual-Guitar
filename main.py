from gesture_player import MusicPlayer
from gesture_detector import GestureDetector
from loop_recorder import LoopRecorder
from config import THIS_DIR, load_mapping

import os
import sys
import cv2
import time
import mediapipe as mp

def main():
    try:
        mapping = load_mapping()
    except Exception as e:
        print(f"[ERROR] Failed to load mapping: {e}")
        sys.exit(1)

    player = MusicPlayer(mapping)
    detector = GestureDetector()
    looper = LoopRecorder()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else 0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam")
        sys.exit(1)

    print("[INFO] Press ESC to quit, 'r' to toggle recording, 'p' to play loop, 's' to save loop")

    active_gestures = set()  # Track currently active gestures

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[WARNING] Failed to grab frame")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            hand_data = detector.detect(rgb_frame)
            gestures = detector.detect_gestures(hand_data)

            for hand in hand_data:
                detector.drawer.draw_landmarks(frame, hand["landmarks"], mp.solutions.hands.HAND_CONNECTIONS)

            # If STOP gesture is detected, stop all sounds and clear active gestures
            if "STOP" in gestures:
                player.stop_all()
                active_gestures.clear()
            else:
                current_gestures = set(gesture for gesture in gestures if gesture in mapping)

                # Play sound only for newly raised gestures (in current_gestures but not in active_gestures)
                new_gestures = current_gestures - active_gestures
                for gesture in new_gestures:
                    player.play(gesture)
                    looper.add_event(gesture)

                # Update active_gestures for next iteration
                active_gestures = current_gestures

            y_offset = 30
            for gesture in gestures:
                cv2.putText(frame, gesture, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                y_offset += 40

            status_text = ""
            if looper.recording:
                status_text = "RECORDING"
                color = (0, 0, 255)
            elif looper.playing:
                status_text = "PLAYING LOOP"
                color = (255, 0, 0)
            else:
                color = (0, 255, 0)

            if status_text:
                cv2.putText(frame, status_text, (10, frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            cv2.imshow("Gesture Music", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                print("[INFO] Exiting...")
                break
            elif key == ord('r'):
                looper.toggle_recording()
                print(f"[INFO] Recording toggled: {'ON' if looper.recording else 'OFF'}")
            elif key == ord('p'):
                print("[INFO] Playing loop")
                looper.play(player)
            elif key == ord('s'):
                save_path = THIS_DIR / "loop.txt"
                looper.save(save_path)
                print(f"[INFO] Loop saved to {save_path}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        if hasattr(player, 'close'):
            player.close()
        print("[INFO] Cleanup done")

if __name__ == "__main__":
    main()
