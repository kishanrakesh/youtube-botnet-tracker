#!/usr/bin/env python3
import cv2, numpy as np                             # ← add numpy
import pandas as pd
from pathlib import Path
import re, sys

CSV_IN   = Path("video_comment_channels.csv")
CSV_OUT  = Path("video_comment_channels_classified.csv")
SHOT_DIR = Path("screenshots")

# ── unchanged helpers ─────────────────────────────────────────────
def filename_to_rownum(fname: str) -> int | None:
    m = re.match(r"(\d+)_", fname)
    return int(m.group(1)) - 1 if m else None

def load_df():
    if not CSV_IN.exists():
        sys.exit("❌  input.csv not found")
    df = pd.read_csv(CSV_IN).reset_index(drop=True)  # ensure RangeIndex
    if "is_bot" not in df.columns:
        df["is_bot"] = ""
    return df

# ── NEW helper: white “done” frame ────────────────────────────────
def done_frame(w: int = 720, h: int = 480) -> "np.ndarray":
    img = np.ones((h, w, 3), dtype=np.uint8) * 255
    msg1 = "All images reviewed!"
    msg2 = "Press  b  to jump to the LAST image"
    msg3 = "Press  q  to save & quit"
    for i, text in enumerate([msg1, msg2, msg3]):
        y = 60 + i * 60
        cv2.putText(img, text, (40, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2,
                    lineType=cv2.LINE_AA)
    return img

# ── main loop ─────────────────────────────────────────────────────
def main():
    df   = load_df()
    pics = sorted(SHOT_DIR.glob("*.png"))
    if not pics:
        sys.exit("❌  No screenshots found")

    cv2.namedWindow("Bot Classifier (y/n/u | b back | q quit)",
                    cv2.WINDOW_NORMAL)

    i            = 0
    total_needed = sum(df["is_bot"] == "")
    processed    = 0

    while 0 <= i <= len(pics):                      # note “<=”
        # ── case 1: all pics done → show summary screen ──────────
        if i == len(pics):
            cv2.setWindowTitle(
                "Bot Classifier (y/n/u | b back | q quit)",
                f"{processed}/{total_needed}  (done)",
            )
            cv2.imshow("Bot Classifier (y/n/u | b back | q quit)",
                       done_frame())
            key = cv2.waitKey(0) & 0xFF
            if key == ord("q"):
                break
            if key == ord("b") and pics:
                i = len(pics) - 1                   # jump to last image
                continue
            else:
                continue                            # ignore other keys

        # ── case 2: normal screenshot ────────────────────────────
        shot    = pics[i]
        row_idx = filename_to_rownum(shot.name)
        if row_idx is None or row_idx >= len(df):
            i += 1
            continue

        img = cv2.imread(str(shot))
        if img is None:
            print(f"⚠️  Couldn’t read {shot.name}")
            i += 1
            continue

        cv2.setWindowTitle(
            "Bot Classifier (y/n/u | b back | q quit)",
            f"{processed}/{total_needed}  {shot.name}",
        )
        cv2.imshow("Bot Classifier (y/n/u | b back | q quit)", img)

        key = cv2.waitKey(0) & 0xFF
        if key == ord("q"):
            break
        if key == ord("b"):
            if i > 0:
                if df.at[row_idx, "is_bot"]:
                    processed -= 1
                df.at[row_idx, "is_bot"] = ""
                i -= 1
            continue
        if key not in (ord("y"), ord("n"), ord("u")):
            continue

        label = {ord("y"): "Y", ord("n"): "N", ord("u"): "U"}[key]
        if not df.at[row_idx, "is_bot"]:
            processed += 1
        df.at[row_idx, "is_bot"] = label
        i += 1                                        # advance

    cv2.destroyAllWindows()
    df.to_csv(CSV_OUT, index=False)
    print(f"\n✅  Labels saved to {CSV_OUT}")

if __name__ == "__main__":
    main()
