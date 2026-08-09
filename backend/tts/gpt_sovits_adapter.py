import os
import sys
import torch
import numpy as np
import soundfile as sf
from typing import Optional

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
gpt_sovits_root = os.path.join(base_dir, "GPT_SoVITS")
gpt_sovits_core = os.path.join(gpt_sovits_root, "GPT_SoVITS")

if gpt_sovits_root not in sys.path:
    sys.path.insert(0, gpt_sovits_root)
if gpt_sovits_core not in sys.path:
    sys.path.insert(0, gpt_sovits_core)

from .base import BaseTTSAdapter

class GPTSoVITSAdapter(BaseTTSAdapter):
    """
    RVC-Boss 公式 GPT-SoVITS v2 エンジンによる本物のゼロショット音声クローンアダプター。
    """

    def __init__(self, device: Optional[str] = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        self.tts_engine = None
        self._is_loaded = False

    def load_model(self):
        if self._is_loaded and self.tts_engine is not None:
            return

        try:
            from TTS_infer_pack.TTS import TTS, TTS_Config

            pretrained_dir = os.path.join(gpt_sovits_core, "pretrained_models")
            fast_langdetect_dir = os.path.join(pretrained_dir, "fast_langdetect")
            os.makedirs(fast_langdetect_dir, exist_ok=True)

            t2s_ckpt = os.path.join(pretrained_dir, "gsv-v2final-pretrained", "s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt")
            vits_pth = os.path.join(pretrained_dir, "gsv-v2final-pretrained", "s2G2333k.pth")

            if not os.path.exists(vits_pth):
                vits_pth = os.path.join(pretrained_dir, "s2G488k.pth")

            print(f"本物の GPT-SoVITS v2 エンジンをロード中... (device: {self.device})")
            print(f"-> GPTモデル: {os.path.basename(t2s_ckpt)}")
            print(f"-> SoVITSモデル: {os.path.basename(vits_pth)}")

            dict_config = {
                "custom": {
                    "version": "v2",
                    "device": self.device,
                    "is_half": False,
                    "t2s_weights_path": t2s_ckpt,
                    "vits_weights_path": vits_pth,
                    "bert_base_path": os.path.join(pretrained_dir, "chinese-roberta-wwm-ext-large"),
                    "cnhuhbert_base_path": os.path.join(pretrained_dir, "chinese-hubert-base")
                }
            }

            config = TTS_Config(dict_config)
            self.tts_engine = TTS(config)
            self._is_loaded = True
            print("本物の GPT-SoVITS エンジンのロードが完了しました！")

        except Exception as e:
            self._is_loaded = False
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"本物の GPT-SoVITS エンジンのロードに失敗しました: {e}")

    def trim_reference_audio_for_gpt_sovits(self, ref_path: str, output_path: str, target_duration: float = 6.0) -> str:
        """
        GPT-SoVITS 推奨仕様(3秒〜10秒)に合わせて参照音声を自動調整する。
        """
        import librosa

        data, sr = librosa.load(ref_path, sr=32000)
        duration = len(data) / sr

        if duration > 10.0 or duration < 3.0:
            target_samples = int(target_duration * sr)
            if len(data) > target_samples:
                start_sample = int(0.5 * sr)
                end_sample = start_sample + target_samples
                data = data[start_sample:end_sample]

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        sf.write(output_path, data, sr)
        return output_path

    def is_available(self) -> bool:
        try:
            from TTS_infer_pack.TTS import TTS
            return True
        except ImportError:
            return False

    def generate(
        self,
        text: str,
        reference_audio_path: str,
        output_path: str,
        language: str = "ja",
        prompt_text: str = "本日はご結婚おめでとうございます。",
        prompt_language: str = "ja"
    ) -> str:
        if not text or not text.strip():
            raise ValueError("原稿テキストが空です。")

        if not os.path.exists(reference_audio_path):
            raise FileNotFoundError(f"参照音声が見つかりません: {reference_audio_path}")

        trimmed_ref_path = reference_audio_path + ".trimmed.wav"
        try:
            ref_to_use = self.trim_reference_audio_for_gpt_sovits(reference_audio_path, trimmed_ref_path, target_duration=6.0)
        except Exception as e:
            ref_to_use = reference_audio_path

        # モデルのロード
        self.load_model()

        print(f"[GPT-SoVITS] 本物の公式エンジンでゼロショットクローン音声生成を開始します...")

        try:
            inputs = {
                "text": text,
                "text_lang": language,
                "ref_audio_path": ref_to_use,
                "prompt_text": prompt_text,
                "prompt_lang": prompt_language,
                "top_k": 5,
                "top_p": 1.0,
                "temperature": 1.0,
                "speed_factor": 1.0
            }

            for sr, audio_data in self.tts_engine.run(inputs):
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                sf.write(output_path, audio_data, sr)
                print(f"[GPT-SoVITS] 本物のクローン音声生成完了: {output_path} (sr={sr})")

                if os.path.exists(trimmed_ref_path):
                    try:
                        os.remove(trimmed_ref_path)
                    except Exception:
                        pass

                return os.path.abspath(output_path)

            raise RuntimeError("音声データの生成ストリームが空でした。")

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"本物の GPT-SoVITS による音声生成中にエラーが発生しました: {e}")
