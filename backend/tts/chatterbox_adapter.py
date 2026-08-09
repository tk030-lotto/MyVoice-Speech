import os
import torch
import soundfile as sf
from typing import Optional

from .base import BaseTTSAdapter
from ..audio.converter import convert_to_wav, change_speech_speed
from ..audio.text_processor import JapaneseTextProcessor

class ChatterboxAdapter(BaseTTSAdapter):
    """
    Chatterbox Multilingual V3 用のTTSアダプター実装 (日本語テキスト・話速最適化対応)
    """

    def __init__(self, device: Optional[str] = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.model = None
        self._is_loaded = False
        self.text_processor = JapaneseTextProcessor()

    def load_model(self):
        if self._is_loaded and self.model is not None:
            return

        try:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            print(f"Chatterbox Multilingual V3 モデルをロード中... (device: {self.device})")
            self.model = ChatterboxMultilingualTTS.from_pretrained(device=self.device)
            self._is_loaded = True
            print("Chatterbox Multilingual V3 モデルのロードが完了しました。")
        except Exception as e:
            self._is_loaded = False
            raise RuntimeError(f"Chatterbox Multilingual V3 モデルのロードに失敗しました: {e}")

    def is_available(self) -> bool:
        try:
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            return True
        except ImportError:
            return False

    def generate(
        self,
        text: str,
        reference_audio_path: str,
        output_path: str,
        language: str = "ja",
        exaggeration: float = 0.3,
        cfg_weight: float = 0.7,
        temperature: float = 0.5,
        repetition_penalty: float = 2.0,
        speed_factor: float = 0.88,
        use_hiragana_reading: bool = False
    ) -> str:
        """
        参照音声と日本語テキストから Chatterbox V3 を呼び出し、自然な話速・イントネーションのWAV音声を出力する。

        :param text: 合成対象の日本語テキスト
        :param reference_audio_path: 本人の参照音声WAVパス
        :param output_path: 生成結果WAVの出力先パス
        :param language: 言語コード ('ja'デフォルト)
        :param speed_factor: 話速 (0.88倍速など落ち着いた速度)
        :param use_hiragana_reading: 漢字読み誤り防止のひらがな化を行うか
        :return: 生成されたWAVファイルの絶対パス
        """
        if not text or not text.strip():
            raise ValueError("原稿テキストが空です。テキストを入力してください。")

        if not os.path.exists(reference_audio_path):
            raise FileNotFoundError(f"参照音声ファイルが見つかりません: {reference_audio_path}")

        # 日本語テキストの最適化 (アクセント歪み防止 & ポーズ挿入)
        if use_hiragana_reading:
            processed_text = self.text_processor.to_hiragana_with_pauses(text)
        else:
            processed_text = self.text_processor.process_for_speech(text, add_pauses=True)

        print(f"最適化されたテキスト: {processed_text}")

        # 前処理: 参照音声を 24kHz WAV に正規化
        normalized_ref_path = reference_audio_path + ".norm.wav"
        try:
            convert_to_wav(reference_audio_path, normalized_ref_path, target_sr=24000)
            ref_path_to_use = normalized_ref_path
        except Exception as e:
            ref_path_to_use = reference_audio_path

        # モデルのロード
        self.load_model()

        temp_output_path = output_path + ".raw.wav"

        print(f"自然な日本語スピーチ音声を生成中... (話速: {speed_factor}x)")
        try:
            wav_tensor = self.model.generate(
                text=processed_text,
                language_id=language,
                audio_prompt_path=ref_path_to_use,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight,
                temperature=temperature,
                repetition_penalty=repetition_penalty
            )

            if isinstance(wav_tensor, torch.Tensor):
                wav_data = wav_tensor.squeeze().cpu().numpy()
            else:
                wav_data = wav_tensor

            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            sr = getattr(self.model, "sr", 24000)
            sf.write(temp_output_path, wav_data, sr)

            # 話速(スピード)の調整 (スピーチ用に落ち着いたペースにアライメント)
            if speed_factor != 1.0:
                change_speech_speed(temp_output_path, output_path, speed_factor=speed_factor)
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
            else:
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_output_path, output_path)

            print(f"スピーチ音声の生成・スピード最適化完了: {output_path}")

            if os.path.exists(normalized_ref_path):
                try:
                    os.remove(normalized_ref_path)
                except Exception:
                    pass

            return os.path.abspath(output_path)

        except Exception as e:
            raise RuntimeError(f"スピーチ音声生成処理中にエラーが発生しました: {e}")
