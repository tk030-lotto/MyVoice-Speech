import os
import numpy as np
import soundfile as sf

def generate_sample_reference_wav(output_path: str = "samples/reference.wav", duration: float = 3.0, sr: int = 24000):
    """
    テスト検証用のサンプル参照音声WAVを生成する。
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    t = np.linspace(0, duration, int(sr * duration), False)
    # 440Hz (A4) の和音・サイン波で音声テスト信号を作成
    audio_data = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.25 * np.sin(2 * np.pi * 880 * t)
    # フェードイン・フェードアウト
    fade_len = int(sr * 0.1)
    audio_data[:fade_len] *= np.linspace(0, 1, fade_len)
    audio_data[-fade_len:] *= np.linspace(1, 0, fade_len)

    sf.write(output_path, audio_data, sr)
    print(f"テスト用サンプル参照音声を生成しました: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_sample_reference_wav()
