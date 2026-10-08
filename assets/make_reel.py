"""카드뉴스 6장 → 인스타 릴스(1080x1920, 9:16) 영상.

사용법:
    python3 make_reel.py <카드폴더> <출력.mp4>
카드폴더 안의 01.png ~ 06.png 를 순서대로 사용한다.
--hook "질문/문구" 를 주면 ("/" 자리에서 줄바꿈) 맨 앞에 1.5초 질문 화면을 넣고 표지는 3초로 줄인다.
표지 3.5초, 기사 카드 4.5초씩, 장 사이 0.5초 크로스페이드, 살짝 확대되는 움직임.
배경음악은 넣지 않는다(무음). 저작권 걱정 없는 음원이 생기면 --music 옵션으로 추가.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from krangi import render_krangi, GOLD, INK  # noqa: E402

W, H = 1080, 1920
BG = (255, 249, 236)
NAVY = (34, 40, 74)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FPS = 30
FADE = 0.5


def frame_for(card_path, idx, total):
    """카드 한 장을 9:16 세로 화면에 배치한다."""
    base = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(base)
    f = ImageFont.truetype(FONT, 52, index=1)
    fs = ImageFont.truetype(FONT, 34, index=1)
    d.text((W // 2, 150), "크랑이뉴스 · 아침 브리핑", font=f, fill=GOLD, anchor="mm")
    card = Image.open(card_path).convert("RGB").resize((1000, 1250), Image.LANCZOS)
    base.paste(card, (40, 260))
    # 진행 점
    y = 1580
    gap = 44
    x0 = W // 2 - gap * (total - 1) // 2
    for i in range(total):
        r = 12 if i == idx else 8
        col = GOLD if i == idx else (120, 126, 160)
        d.ellipse([x0 + i * gap - r, y - r, x0 + i * gap + r, y + r], fill=col)
    msg = "끝까지 보면 내 생활 꿀팁까지!" if idx == 0 else ("필요한 친구에게 보내주고, 저장해두기" if idx == total - 1 else "")
    if msg:
        d.text((W // 2, 1680), msg, font=fs, fill=(230, 232, 245), anchor="mm")
    if idx == 0:
        k = render_krangi(260, "happy")
        base.paste(k, (W - k.width - 30, H - k.height - 20), k)
    return base


def hook_frame(question, expr="surprised"):
    """첫 1.5초: 화면 가득 큰 질문 한 줄 + 크랑이. 스크롤을 멈추게 하는 용도."""
    from card_template import wrap
    base = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(base)
    fs = ImageFont.truetype(FONT, 40, index=1)
    d.text((W // 2, 300), "오늘 아침 1분 경제", font=fs, fill=GOLD, anchor="mm")
    fq = ImageFont.truetype(FONT, 96, index=1)
    lines = wrap(d, question.replace("/", "\n"), fq, W - 140)[:3]  # "/" 로 줄바꿈 위치 지정
    lh = int(fq.size * 1.35)
    y = 760 - lh * len(lines) // 2
    for ln in lines:
        d.text((W // 2, y), ln, font=fq, fill=(255, 255, 255), anchor="mm")
        y += lh
    k = render_krangi(460, expr)
    base.paste(k, ((W - k.width) // 2, H - k.height - 180), k)
    return base


def main(card_dir, out, music=None, hook=None):
    cards = [os.path.join(card_dir, f"{i:02d}.png") for i in range(1, 7)]
    cards = [c for c in cards if os.path.exists(c)]
    if len(cards) < 2:
        raise SystemExit("카드가 2장 이상 필요해요")
    durs = [3.5] + [4.5] * (len(cards) - 1)
    tmp = tempfile.mkdtemp()
    frames = [frame_for(c, i, len(cards)) for i, c in enumerate(cards)]
    if hook:
        frames.insert(0, hook_frame(hook))
        durs = [1.5, 3.0] + durs[1:]
    inputs, filters = [], []
    for i, fr in enumerate(frames):
        p = os.path.join(tmp, f"f{i}.png")
        fr.save(p)
        inputs += ["-loop", "1", "-t", str(durs[i]), "-i", p]
        n = int(durs[i] * FPS)
        # 1.0 → 1.04 로 천천히 확대
        filters.append(
            f"[{i}:v]scale=2160:3840,zoompan=z='1+0.04*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={n}:s={W}x{H}:fps={FPS},format=yuv420p,setsar=1[v{i}]"
        )
    # 크로스페이드 연결
    prev = "v0"
    offset = 0.0
    for i in range(1, len(frames)):
        offset += durs[i - 1] - FADE
        outl = f"x{i}"
        filters.append(f"[{prev}][v{i}]xfade=transition=slideleft:duration={FADE}:offset={offset:.2f}[{outl}]")
        prev = outl
    total = sum(durs) - FADE * (len(frames) - 1)
    cmd = ["ffmpeg", "-y", *inputs]
    if music:
        cmd += ["-i", music]
    cmd += ["-filter_complex", ";".join(filters), "-map", f"[{prev}]"]
    if music:
        cmd += ["-map", f"{len(frames)}:a", "-af", f"afade=t=out:st={total-1.5:.2f}:d=1.5", "-shortest", "-c:a", "aac", "-b:a", "128k"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
            "-r", str(FPS), "-t", f"{total:.2f}", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(out, f"{total:.1f}s")


if __name__ == "__main__":
    args = sys.argv[1:]
    music = hook = None
    if "--hook" in args:
        i = args.index("--hook")
        hook = args[i + 1]
        del args[i:i + 2]
    if "--music" in args:
        i = args.index("--music")
        music = args[i + 1]
        del args[i:i + 2]
    main(args[0], args[1], music, hook)
