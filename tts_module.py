"""
TTS语音模块
作者：D
功能说明：使用pyttsx3朗读单词发音
"""

import threading


def speak_word(word):
    """在子线程中朗读单词，不阻塞主界面"""
    def _speak():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(word)
            engine.runAndWait()
        except Exception as e:
            print(f"发音失败: {e}")
    
    thread = threading.Thread(target=_speak, daemon=True)
    thread.start()


# 单独测试入口
if __name__ == "__main__":
    speak_word("abandon")
    # 等待发音完成（测试用，实际项目中不需要）
    import time
    time.sleep(3)