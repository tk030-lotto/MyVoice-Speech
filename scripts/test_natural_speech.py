import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.tts import ChatterboxAdapter

def main():
    parser = argparse.ArgumentParser(description="MyVoice Speech - 自然なスピーチ音速・イントネーション検証スクリプト")
    parser.add_argument("--ref", type=str, default="samples/my_voice.wav", help="参照音声WAVパス")
    parser.add_argument("--text", type=str, default="本日は、ご結婚、おめでとうございます。新郎の父でございます。二人の新しい門出を、心よりお祝い申し上げます。", help="合成テキスト")
    args = parser.parse_args()

    ref_audio = args.ref
    if not os.path.exists(ref_audio):
        print(f"エラー: 参照音声 {ref_audio} が見つかりません。")
        sys.exit(1)

    adapter = ChatterboxAdapter()

    print("==================================================")
    print("MyVoice Speech - 自然なスピーチ音声生成テスト開始")
    print("==================================================")

    # 1. 落ち着いた間＋0.85倍速
    output1 = "backend/outputs/natural_speech_calm.wav"
    print("\n--- [1. 自然なポーズ + 0.85倍落ち着いた話速] 生成中 ---")
    adapter.generate(
        text=args.text,
        reference_audio_path=ref_audio,
        output_path=output1,
        language="ja",
        exaggeration=0.25,
        cfg_weight=0.75,
        temperature=0.4,
        speed_factor=0.85,
        use_hiragana_reading=False
    )

    # 2. 平仮名ルビ補助＋0.88倍速
    output2 = "backend/outputs/natural_speech_hiragana.wav"
    print("\n--- [2. 平仮名ルビアクセント補助 + 0.88倍話速] 生成中 ---")
    adapter.generate(
        text=args.text,
        reference_audio_path=ref_audio,
        output_path=output2,
        language="ja",
        exaggeration=0.25,
        cfg_weight=0.75,
        temperature=0.4,
        speed_factor=0.88,
        use_hiragana_reading=True
    )

    print("\n==================================================")
    print("自然なスピーチ音声の生成が完了しました！")
    print("==================================================")

if __name__ == "__main__":
    main()
