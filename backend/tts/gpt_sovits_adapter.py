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
        self._whisper_model = None

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

    def prepare_reference_audio_and_prompt(
        self,
        ref_path: str,
        output_trimmed_path: str,
        target_min_sec: float = 3.5,
        target_max_sec: float = 7.5
    ) -> tuple[str, str]:
        """
        VAD (無音検出) によるスマートトリミングと Whisper (STT) による参照テキスト自動生成を行い、
        GPT-SoVITS ゼロショットTTSのコンテキスト精度を極限まで高める。
        """
        import librosa

        print(f"[GPT-SoVITS] 参照音声を最適化処理中: {ref_path}")
        y, sr = librosa.load(ref_path, sr=32000)

        # VAD: 無音検出で発話区間を切り出し
        intervals = librosa.effects.split(y, top_db=25, frame_length=2048, hop_length=512)

        blocks = []
        if len(intervals) > 0:
            cur_start, cur_end = intervals[0]
            for next_start, next_end in intervals[1:]:
                # 発話間隔が0.3秒以下の場合は同じ文・フレーズとして結合
                if (next_start - cur_end) / sr <= 0.3:
                    cur_end = next_end
                else:
                    blocks.append((cur_start, cur_end))
                    cur_start, cur_end = next_start, next_end
            blocks.append((cur_start, cur_end))

        best_start, best_end = 0, len(y)
        for s, e in blocks:
            dur = (e - s) / sr
            if target_min_sec <= dur <= target_max_sec:
                best_start, best_end = s, e
                break

        if best_start == 0 and best_end == len(y) and len(blocks) > 0:
            accum_s, accum_e = blocks[0]
            for s, e in blocks[1:]:
                if (e - accum_s) / sr <= target_max_sec:
                    accum_e = e
                else:
                    break
            best_start, best_end = accum_s, accum_e

        # 前後に 0.1 秒のマージンを設ける
        pad_s = max(0, int(best_start - 0.1 * sr))
        pad_e = min(len(y), int(best_end + 0.1 * sr))

        trimmed_audio = y[pad_s:pad_e]
        trimmed_duration = len(trimmed_audio) / sr

        os.makedirs(os.path.dirname(os.path.abspath(output_trimmed_path)), exist_ok=True)
        sf.write(output_trimmed_path, trimmed_audio, sr)
        print(f"[GPT-SoVITS] VADスマートトリミング完了: {pad_s/sr:.2f}s ~ {pad_e/sr:.2f}s (長さ: {trimmed_duration:.2f}秒)")

        # Whisper による自動文字起こし (prompt_text)
        try:
            from faster_whisper import WhisperModel
            if self._whisper_model is None:
                print("[GPT-SoVITS] 自動文字起こし用 Faster-Whisper (small) を準備中...")
                self._whisper_model = WhisperModel("small", device="cpu", compute_type="int8")

            segments, _ = self._whisper_model.transcribe(output_trimmed_path, language="ja")
            prompt_text = "".join([seg.text for seg in segments]).strip()
            print(f"[GPT-SoVITS] 自動文字起こし成功: '{prompt_text}'")
        except Exception as e:
            print(f"[GPT-SoVITS] 警告: Whisperによる文字起こしに失敗しました ({e})。デフォルト値を使用します。")
            prompt_text = "ただいまご紹介に預かりました新郎の父と申します。"

        return output_trimmed_path, prompt_text

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
        prompt_text: Optional[str] = None,
        prompt_language: str = "ja",
        top_k: int = 15,
        top_p: float = 1.0,
        temperature: float = 0.8,
        speed_factor: float = 1.0
    ) -> str:
        if not text or not text.strip():
            raise ValueError("原稿テキストが空です。")

        if not os.path.exists(reference_audio_path):
            raise FileNotFoundError(f"参照音声が見つかりません: {reference_audio_path}")

        trimmed_ref_path = reference_audio_path + ".trimmed.wav"
        
        # 参照テキストが明示されていない場合は、VAD+Whisperで最適なセリフと音声を抽出
        if prompt_text is None or not prompt_text.strip():
            try:
                ref_to_use, auto_prompt_text = self.prepare_reference_audio_and_prompt(
                    reference_audio_path, trimmed_ref_path
                )
                prompt_text = auto_prompt_text
            except Exception as e:
                print(f"[GPT-SoVITS] 参照音声の事前処理中にエラー: {e}")
                ref_to_use = reference_audio_path
                prompt_text = "ただいまご紹介に預かりました。"
        else:
            ref_to_use = reference_audio_path

        # モデルのロード
        self.load_model()

        print(f"[GPT-SoVITS] 公式エンジンでゼロショットクローン音声生成を開始します...")
        print(f"-> 参照音声: {os.path.basename(ref_to_use)}")
        print(f"-> 参照テキスト (prompt_text): '{prompt_text}'")
        print(f"-> 推論パラメータ: top_k={top_k}, top_p={top_p}, temp={temperature}, speed={speed_factor}")

        try:
            inputs = {
                "text": text,
                "text_lang": language,
                "ref_audio_path": ref_to_use,
                "prompt_text": prompt_text,
                "prompt_lang": prompt_language,
                "top_k": top_k,
                "top_p": top_p,
                "temperature": temperature,
                "speed_factor": speed_factor
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

