import time
import json
from pynput import keyboard

class TypingRecorder:
    def __init__(self):
        self.keystroke_log = []
        self.words = []
        self.current_word = ""
        self.current_word_start_time = None
        self.last_key_time = None
        self.backspace_count = 0
        self.session_start_time = None
        self.session_data = None  # NEW: Store full session

    def on_press(self, key):
        now = time.time()

        if self.session_start_time is None:
            self.session_start_time = now

        pause_duration = None
        if self.last_key_time is not None:
            pause_duration = now - self.last_key_time
        self.last_key_time = now

        key_info = {
            "timestamp": now,
            "pause_since_last": pause_duration,
            "key": None,
            "is_special": False
        }

        try:
            char = key.char
            key_info["key"] = char
            self.current_word += char

            if self.current_word_start_time is None:
                self.current_word_start_time = now

        except AttributeError:
            key_info["is_special"] = True

            if key == keyboard.Key.space:
                key_info["key"] = "space"
                self._finalize_word(now)
            elif key == keyboard.Key.backspace:
                key_info["key"] = "backspace"
                if self.current_word:
                    self.current_word = self.current_word[:-1]
                self.backspace_count += 1
            elif key == keyboard.Key.enter:
                key_info["key"] = "enter"
                self._finalize_word(now)
            elif key == keyboard.Key.esc:
                self._finalize_word(now)
                return False

        self.keystroke_log.append(key_info)

    def _finalize_word(self, now):
        if self.current_word:
            self.words.append({
                "word": self.current_word,
                "start_time": self.current_word_start_time,
                "end_time": now,
                "duration": now - self.current_word_start_time,
                "pause_before": None if len(self.words) == 0 else self.current_word_start_time - self.words[-1]["end_time"],
                "backspaces": self.backspace_count
            })
        self.current_word = ""
        self.current_word_start_time = None
        self.backspace_count = 0

    def run(self, output_file=None):
        print("Start typing your essay. Press ESC to stop recording.\n")
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

        session_end_time = time.time()
        self.session_data = {
            "session_start_time": self.session_start_time,
            "session_end_time": session_end_time,
            "duration_seconds": session_end_time - self.session_start_time,
            "keystrokes": self.keystroke_log,
            "words": self.words
        }

        if output_file is None:
            output_file = f"step1_typing_log_{int(self.session_start_time)}.json"

        with open(output_file, "w") as f:
            json.dump(self.session_data, f, indent=4)

        print(f"\nTyping session saved to {output_file}")

    def get_log(self):  # ✅ Required for main.py
        return self.session_data


if __name__ == "__main__":
    recorder = TypingRecorder()
    recorder.run()
