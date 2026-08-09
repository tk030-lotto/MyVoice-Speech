import os
import numpy as np
import soundfile as sf

def convert_to_wav(input_path: str, output_path: str, target_sr: int = 24000) -> str:
    """
    音声ファイルを読み込み、指定されたサンプリングレートのモノラルWAVファイルへ変換・保存する。

    :param input_path: 入力音声ファイルパス
    :param output_path: 変換後WAVファイル保存先
    :param target_sr: サンプリングレート (デフォルト: 24000Hz)
    :return: 変換後WAVファイルのパス
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"音声ファイルが見つかりません: {input_path}")

    data, sr = sf.read(input_path)

    # ステレオからモノラル変換
    if data.ndim > 1:
        data = np.mean(data, axis=1)

    # サンプリングレート変換 (簡単なリサンプリング)
    if sr != target_sr:
        from scipy import signal
        num_samples = int(len(data) * float(target_sr) / sr)
        data = signal.resample(data, num_samples)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, data, target_sr)
    return output_path
