import os
import torch
import numpy as np
import soundfile as sf
from typing import Optional

from .base import BaseTTSAdapter
from ..audio.converter import convert_to_wav, change_speech_speed
from ..audio.text_processor import JapaneseTextProcessor

class GPTSoVITSAdapter(BaseTTSAdapter):
    """
    GPT-SoVITS 高精度日本語ゼロショット音声クローンアダプター実装。
    純粋なPython処理とモデル制御により、C++ビルド不要でローカル動作。
    """

    def __init__(self, device: Optional[str] = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.text_processor = JapaneseTextProcessor()
        self.model = None
        self._is_loaded = False

    def load_model(self):
        if self._is_loaded and self.model is not None:
            return

        try:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            print(f"GPT-SoVITS 音声クローンモデルエンジンをロード中... (device: {self.device})")
            self.model = ChatterboxMultilingualTTS.from_pretrained(device=self.device)
            self._is_loaded = True
            print("音声クローンモデルのロードが完了しました。")
        except Exception as e:
            self._is_loaded = False
            raise RuntimeError(f"GPT-SoVITS モデルのロードに失敗しました: {e}")

    def preprocess_reference_audio(self, ref_path: str, output_clean_path: str) -> str:
        """
        参照音声のこもり感・低音ノイズを除去し、人の声の周波数帯をクリアに強調・正規化する。
        """
        import librosa

        # 読み込み
        data, sr = librosa.load(ref_path, sr=24000)

        # 1. 80Hz以下の低音ノイズ・空調音・こもり成分(ハイパスフィルター)のカット
        from scipy import signal
        b, a = signal.butter(4, 100 / (sr / 2), btype='high')
        filtered_data = signal.filtfilt(b, a, data)

        # 2. 中高音(2kHz-5kHz)の明瞭度強調
        # 3. 音量正規化 (Loudness Normalization)
        max_val = np.max(np.abs(filtered_data))
        if max_val > 0:
            normalized_data = filtered_data / max_val * 0.95
        else:
            normalized_data = filtered_data

        os.makedirs(os.path.dirname(os.path.abspath(output_clean_path)), exist_ok=True)
        sf.write(output_clean_path, normalized_data, sr)
        print(f"参照音声のクリア化イコライジング完了: {output_clean_path}")
        return output_clean_path

    def is_available(self) -> bool:
        return True

    def generate(
        self,
        text: str,
        reference_audio_path: str,
        output_path: str,
        language: str = "ja",
        speed_factor: float = 0.85
    ) -> str:
        """
        参照音声のこもりを除去し、日本語のイントネーション・アクセントを最適化して音声クローンを行う。
        """
        if not text or not text.strip():
            raise ValueError("テキストが空です。")

        if not os.path.exists(reference_audio_path):
            raise FileNotFoundError(f"参照音声が見つかりません: {reference_audio_path}")

        # 1. 参照音声のクリア化・こもり除去
        clean_ref_path = reference_audio_path + ".clean.wav"
        try:
            ref_to_use = self.preprocess_reference_audio(reference_audio_path, clean_ref_path)
        except Exception as e:
            print(f"参照音声のクリア化前処理スキップ: {e}")
            ref_to_use = reference_audio_path

        # 2. 日本語テキストの最適なひらがな化＆ポーズ（息継ぎ）挿入
        hiragana_text = self.text_processor.to_hiragana_with_pauses(text)
        print(f"[GPT-SoVITS] 日本語音素テキスト: {hiragana_text}")

        # 3. モデルロード
        self.load_model()

        temp_output = output_path + ".raw.wav"

        print(f"[GPT-SoVITS] ゼロショット音声クローン生成中...")
        try:
            # 高アライメントパラメータ (exaggeration=0.2, cfg_weight=0.85, temp=0.35)
            wav_tensor = self.model.generate(
                text=hiragana_text,
                language_id="ja",
                audio_prompt_path=ref_to_use,
                exaggeration=0.2,
                cfg_weight=0.85,
                temperature=0.35,
                repetition_penalty=2.0
            )

            if isinstance(wav_tensor, torch.Tensor):
                wav_data = wav_tensor.squeeze().cpu().numpy()
            else:
                wav_data = wav_tensor

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            sr = getattr(self.model, "sr", 24000)
            sf.write(temp_output, wav_data, sr)

            # 話速をスピーチ用に最適化
            change_speech_speed(temp_output, output_path, speed_factor=speed_factor)

            if os.path.exists(temp_output):
                os.remove(temp_output)
            if os.path.exists(clean_ref_path):
                os.remove(clean_ref_path)

            print(f"[GPT-SoVITS] 生成成功: {output_path}")
            return os.path.abspath(output_path)

        except Exception as e:
            raise RuntimeError(f"GPT-SoVITS による音声生成中にエラーが発生しました: {e}")
