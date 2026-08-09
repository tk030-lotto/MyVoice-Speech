import os
import torch
import soundfile as sf
from typing import Optional

from .base import BaseTTSAdapter
from ..audio.converter import convert_to_wav

class ChatterboxAdapter(BaseTTSAdapter):
    """
    Chatterbox Multilingual V3 用のTTSアダプター実装。
    """

    def __init__(self, device: Optional[str] = None):
        """
        :param device: "cuda" または "cpu"。未指定の場合は自動判定。
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.model = None
        self._is_loaded = False

    def load_model(self):
        """
        モデルをローカル環境にロードする (遅延ロード)。
        """
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
        """
        エンジンが利用可能かを返す。
        """
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
        language: str = "ja"
    ) -> str:
        """
        参照音声と日本語テキストから Chatterbox V3 を呼び出し、WAV音声を出力する。

        :param text: 合成対象の日本語テキスト
        :param reference_audio_path: 本人の参照音声WAVパス
        :param output_path: 生成結果WAVの出力先パス
        :param language: 言語コード ('ja'デフォルト)
        :return: 生成されたWAVファイルの絶対パス
        """
        if not text or not text.strip():
            raise ValueError("原稿テキストが空です。テキストを入力してください。")

        if not os.path.exists(reference_audio_path):
            raise FileNotFoundError(f"参照音声ファイルが見つかりません: {reference_audio_path}")

        # 前処理: 参照音声を適切なフォーマット (24kHz WAV) に正規化
        normalized_ref_path = reference_audio_path + ".norm.wav"
        try:
            convert_to_wav(reference_audio_path, normalized_ref_path, target_sr=24000)
            ref_path_to_use = normalized_ref_path
        except Exception as e:
            print(f"参照音声の正規化前処理をスキップしました (直接利用): {e}")
            ref_path_to_use = reference_audio_path

        # モデルのロード
        self.load_model()

        print(f"音声生成を開始します... (言語: {language}, 文字数: {len(text)})")
        try:
            # Chatterbox Multilingual V3 generate 呼び出し
            wav_tensor = self.model.generate(
                text=text,
                language_id=language,
                audio_prompt_path=ref_path_to_use
            )

            # Tensor -> NumPy 変換
            if isinstance(wav_tensor, torch.Tensor):
                wav_data = wav_tensor.squeeze().cpu().numpy()
            else:
                wav_data = wav_tensor

            # 出力ディレクトリ作成 & WAV保存
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            sr = getattr(self.model, "sr", 24000)
            sf.write(output_path, wav_data, sr)

            print(f"音声生成完了: {output_path}")

            # 一時正規化ファイルのクリーンアップ
            if os.path.exists(normalized_ref_path):
                try:
                    os.remove(normalized_ref_path)
                except Exception:
                    pass

            return os.path.abspath(output_path)

        except Exception as e:
            raise RuntimeError(f"Chatterbox による音声生成処理中にエラーが発生しました: {e}")
