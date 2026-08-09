import re
import pykakasi

class JapaneseTextProcessor:
    """
    日本語スピーチテキストの前処理・最適化ユーティリティ。
    AI音声合成が自然なアクセント・イントネーション・間(ポーズ)で発声できるようテキストを調整する。
    """

    def __init__(self):
        self.kks = pykakasi.kakasi()

    def process_for_speech(self, text: str, add_pauses: bool = True) -> str:
        """
        テキストに適切な読点・ポーズを挿入し、読み誤りを防ぐフォーマットを行う。

        :param text: 原稿テキスト
        :param add_pauses: 読点やスペースによる間を強調するかどうか
        :return: 音声合成に最適化されたテキスト
        """
        if not text:
            return ""

        # 余分な空白の削除
        text = text.strip()

        # 読点・句点の強調 (息継ぎ・間を作る)
        if add_pauses:
            # 句点の後に少し大きなポーズ
            text = text.replace("。", "。 ")
            # 読点の後にポーズ
            text = text.replace("、", "、 ")

        return text

    def to_hiragana_with_pauses(self, text: str) -> str:
        """
        漢字の読み誤りを防ぐため、ひらがなに変換しつつ読点・ポーズを維持する。
        """
        result = self.kks.convert(text)
        hiragana_text = "".join([item["hira"] for item in result])
        
        # 句読点の後に適度な間を追加
        hiragana_text = re.sub(r'([。！？])', r'\1 ', hiragana_text)
        hiragana_text = re.sub(r'([、,])', r'\1 ', hiragana_text)

        return hiragana_text
