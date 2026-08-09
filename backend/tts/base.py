import os
from abc import ABC, abstractmethod

class BaseTTSAdapter(ABC):
    """
    音声合成エンジンの抽象基底クラス。
    将来的な他OSSエンジン (GPT-SoVITS, OpenVoice等) への交換を考慮した設計。
    """

    @abstractmethod
    def generate(
        self,
        text: str,
        reference_audio_path: str,
        output_path: str,
        language: str = "ja"
    ) -> str:
        """
        参照音声とテキストから音声WAVを生成し、指定パスに保存する。

        :param text: 合成する日本語テキスト
        :param reference_audio_path: 本人の参照音声WAVファイルのパス
        :param output_path: 出力先WAVファイルのパス
        :param language: 言語ID (デフォルト: 'ja')
        :return: 生成されたWAVファイルの絶対パス
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        エンジンが利用可能かチェックする。
        """
        pass
