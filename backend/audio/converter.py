import os
import subprocess
import numpy as np
import soundfile as sf

def convert_to_wav(input_path: str, output_path: str, target_sr: int = 24000) -> str:
    """
    各種音声ファイル(WAV, M4A, MP3等)を読み込み、24000HzモノラルのWAVファイルへ変換・保存する。
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"音声ファイルが見つかりません: {input_path}")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    try:
        data, sr = sf.read(input_path)
        if data.ndim > 1:
            data = np.mean(data, axis=1)

        if sr != target_sr:
            from scipy import signal
            num_samples = int(len(data) * float(target_sr) / sr)
            data = signal.resample(data, num_samples)

        sf.write(output_path, data, target_sr)
        return output_path
    except Exception as sf_err:
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            cmd = [
                ffmpeg_exe, "-y", "-i", input_path,
                "-ar", str(target_sr), "-ac", "1", output_path
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_path
        except Exception as ffmpeg_err:
            raise RuntimeError(f"音声ファイルのWAV変換に失敗しました ({input_path}): {ffmpeg_err}")

def change_speech_speed(input_wav_path: str, output_wav_path: str, speed_factor: float = 0.88) -> str:
    """
    音声WAVファイルの話速(スピード)を自然に調整する。
    :param speed_factor: 1.0より小さいとゆっくり(例: 0.88倍速)、大きいと早口
    """
    if not os.path.exists(input_wav_path):
        raise FileNotFoundError(f"入力WAVファイルが見つかりません: {input_wav_path}")

    import librosa

    data, sr = librosa.load(input_wav_path, sr=None)
    # librosa.effects.time_stretch によるピッチ保持型速度変更
    stretched_data = librosa.effects.time_stretch(data, rate=speed_factor)

    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    sf.write(output_wav_path, stretched_data, sr)
    return output_wav_path
