import mediapipe as mp

class GestureDetector:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.drawer = mp.solutions.drawing_utils

    def detect(self, image):
        results = self.hands.process(image)
        hand_data = []

        if results.multi_hand_landmarks and results.multi_handedness:
            for landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_data.append({
                    "landmarks": landmarks,
                    "handedness": handedness.classification
                })

        return hand_data

    def detect_gestures(self, hand_data):
        gestures = []

        for hand in hand_data:
            hand_label = hand["handedness"][0].label[0].upper()  # 'L' or 'R'
            fingers_up = []

            finger_indices = {
                "I": 8,
                "M": 12
            }

            try:
                raw_landmarks = hand["landmarks"]
                landmarks = raw_landmarks.landmark

                for label, tip_idx in finger_indices.items():
                    pip_idx = tip_idx - 2
                    if tip_idx >= len(landmarks) or pip_idx < 0:
                        continue

                    tip = landmarks[tip_idx]
                    pip = landmarks[pip_idx]

                    if tip.y < pip.y - 0.02:
                        fingers_up.append(label)

                # Sort to make consistent gesture names like I+M
                if fingers_up:
                    gesture = f"{hand_label}:{'+'.join(sorted(fingers_up))}"
                    gestures.append(gesture)
                else:
                    gestures.append("STOP")

            except Exception as e:
                print(f"[WARNING] Gesture detection failed: {e}")
                continue

        return gestures
