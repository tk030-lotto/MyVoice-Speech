import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.tts import ChatterboxAdapter

def main():
    parser = argparse.ArgumentParser(description="MyVoice Speech - パラメータチューニング比較生成スクリプト")
    parser.add_argument("--ref", type=str, default="samples/my_voice.wav", help="参照音声WAVパス")
    parser.add_argument("--text", type=str, default="本日はご結婚おめでとうございます。新郎の父でございます。二人の新しい門出を心よりお祝い申し上げます。", help="合成テキスト")
    args = parser.parse_args()

    ref_audio = args.ref
    if not os.path.exists(ref_audio):
        print(f"エラー: 参照音声 {ref_audio} が見つかりません。")
        sys.exit(1)

    patterns = [
        {
            "name": "pattern_A_default",
            "desc": "パターンA (標準パラメータ)",
            "file": "backend/outputs/pattern_A_default.wav",
            "params": {"exaggeration": 0.5, "cfg_weight": 0.5, "temperature": 0.8}
        },
        {
            "name": "pattern_B_calm_speech",
            "desc": "パターンB (落ち着いたスピーチ調: 抑揚低め/参照再現強め)",
            "file": "backend/outputs/pattern_B_calm_speech.wav",
            "params": {"exaggeration": 0.25, "cfg_weight": 0.7, "temperature": 0.5}
        },
        {
            "name": "pattern_C_voice_fidelity",
            "desc": "パターンC (声質再現最重視: 参照忠実度MAX)",
            "file": "backend/outputs/pattern_C_voice_fidelity.wav",
            "params": {"exaggeration": 0.35, "cfg_weight": 0.9, "temperature": 0.4}
        },
        {
            "name": "pattern_D_stable_tone",
            "desc": "パターンD (自然・安定度重視: 低ランダム/フラットトーン)",
            "file": "backend/outputs/pattern_D_stable_tone.wav",
            "params": {"exaggeration": 0.15, "cfg_weight": 0.8, "temperature": 0.3}
        }
    ]

    print("==================================================")
    print("MyVoice Speech - パラメータチューニング比較生成開始")
    print("==================================================")

    adapter = ChatterboxAdapter()

    for p in patterns:
        print(f"\n--- [{p['desc']}] 生成中 ---")
        try:
            output_file = adapter.generate(
                text=args.text,
                reference_audio_path=ref_audio,
                output_path=p["file"],
                language="ja",
                **p["params"]
            )
            print(f"成功: {output_file} (サイズ: {os.path.getsize(output_file)/1024.0:.1f} KB)")
        except Exception as e:
            print(f"失敗 [{p['name']}]: {e}")

    print("\n==================================================")
    print("全4パターンの比較生成が完了しました！")
    print("==================================================")

if __name__ == "__main__":
    main()
