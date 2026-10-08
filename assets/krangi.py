"""크랑이(동전 요정) 캐릭터 그리기 모듈.

카드뉴스·릴스 제작 시 import 해서 사용한다.
    from krangi import render_krangi
    img = render_krangi(size=400, expr="happy")   # RGBA 투명 배경
표정: basic, happy, surprised, worried, wink
"""
import math
from PIL import Image, ImageDraw

GOLD = (246, 190, 52)
GOLD_DARK = (190, 132, 22)
GOLD_LINE = (217, 154, 34)
INK = (58, 42, 18)
CHEEK = (240, 124, 90, 150)
WHITE = (255, 255, 255)

SS = 4  # 슈퍼샘플링 배율 (부드러운 외곽선)


def _arc_line(d, box, start, end, width, fill):
    d.arc(box, start, end, fill=fill, width=width)


def render_krangi(size=400, expr="basic"):
    S = size * SS
    img = Image.new("RGBA", (S, int(S * 1.15)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx, cy = S / 2, S * 0.62
    r = S * 0.36
    lw = max(2, int(S * 0.018))

    # 팔
    arm = int(S * 0.022)
    if expr in ("happy", "surprised"):
        d.line([(cx - r * 0.95, cy + r * 0.05), (cx - r * 1.3, cy - r * 0.55)], fill=GOLD_DARK, width=arm, joint="curve")
        d.line([(cx + r * 0.95, cy + r * 0.05), (cx + r * 1.3, cy - r * 0.55)], fill=GOLD_DARK, width=arm, joint="curve")
    elif expr == "worried":
        d.line([(cx - r * 0.95, cy + r * 0.1), (cx - r * 0.55, cy + r * 0.55)], fill=GOLD_DARK, width=arm)
        d.line([(cx + r * 0.95, cy + r * 0.1), (cx + r * 0.55, cy + r * 0.55)], fill=GOLD_DARK, width=arm)
    else:
        d.line([(cx - r * 0.95, cy + r * 0.1), (cx - r * 1.3, cy + r * 0.45)], fill=GOLD_DARK, width=arm)
        d.line([(cx + r * 0.95, cy + r * 0.1), (cx + r * 1.3, cy - r * 0.45)], fill=GOLD_DARK, width=arm)

    # 머리 위 반짝 뿔
    tip = (cx, cy - r * 1.42)
    d.polygon([(cx - r * 0.16, cy - r * 0.96), tip, (cx + r * 0.16, cy - r * 0.96)], fill=GOLD, outline=GOLD_DARK, width=lw)
    d.ellipse([tip[0] - r * 0.07, tip[1] - r * 0.07, tip[0] + r * 0.07, tip[1] + r * 0.07], fill=WHITE)

    # 몸통(동전)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=GOLD_DARK, width=lw * 2)
    ir = r * 0.8
    n = 36
    for i in range(n):
        if i % 2:
            continue
        a0, a1 = 360 / n * i, 360 / n * (i + 1)
        _arc_line(d, [cx - ir, cy - ir, cx + ir, cy + ir], a0, a1, lw, GOLD_LINE)
    # 하이라이트
    d.arc([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86], 200, 245, fill=(255, 236, 170), width=int(lw * 1.6))

    # 볼터치
    for sx in (-1, 1):
        ex = cx + sx * r * 0.5
        d.ellipse([ex - r * 0.15, cy + r * 0.12, ex + r * 0.15, cy + r * 0.26], fill=CHEEK)

    # 눈
    ey = cy - r * 0.12
    for sx in (-1, 1):
        ex = cx + sx * r * 0.32
        if expr == "happy" or (expr == "wink" and sx == 1):
            d.arc([ex - r * 0.13, ey - r * 0.1, ex + r * 0.13, ey + r * 0.14], 200, 340, fill=INK, width=int(lw * 1.4))
        elif expr == "surprised":
            d.ellipse([ex - r * 0.13, ey - r * 0.17, ex + r * 0.13, ey + r * 0.17], fill=WHITE, outline=INK, width=lw)
            d.ellipse([ex - r * 0.07, ey - r * 0.07, ex + r * 0.07, ey + r * 0.07], fill=INK)
        else:
            d.ellipse([ex - r * 0.11, ey - r * 0.15, ex + r * 0.11, ey + r * 0.15], fill=INK)
            d.ellipse([ex - r * 0.02, ey - r * 0.11, ex + r * 0.06, ey - r * 0.03], fill=WHITE)
        if expr == "worried":
            d.line([(ex - sx * r * 0.14, ey - r * 0.3), (ex + sx * r * 0.1, ey - r * 0.22)], fill=INK, width=lw)

    # 입
    my = cy + r * 0.22
    if expr == "surprised":
        d.ellipse([cx - r * 0.09, my - r * 0.06, cx + r * 0.09, my + r * 0.16], fill=INK)
    elif expr == "worried":
        d.arc([cx - r * 0.14, my + r * 0.02, cx + r * 0.14, my + r * 0.2], 200, 340, fill=INK, width=int(lw * 1.3))
    elif expr == "happy":
        d.chord([cx - r * 0.17, my - r * 0.1, cx + r * 0.17, my + r * 0.2], 0, 180, fill=INK)
        d.chord([cx - r * 0.09, my + r * 0.04, cx + r * 0.09, my + r * 0.18], 0, 180, fill=(240, 110, 90))
    else:
        d.arc([cx - r * 0.15, my - r * 0.12, cx + r * 0.15, my + r * 0.12], 20, 160, fill=INK, width=int(lw * 1.3))

    out = img.resize((size, int(size * 1.15)), Image.LANCZOS)
    return out


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "krangi_sheet.png"
    from PIL import ImageFont
    font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
    exprs = [("basic", "기본"), ("happy", "좋은 소식"), ("surprised", "깜짝 뉴스"), ("worried", "걱정 뉴스"), ("wink", "꿀팁")]
    W, H = 1600, 600
    sheet = Image.new("RGB", (W, H), (255, 249, 236))
    sd = ImageDraw.Draw(sheet)
    tf = ImageFont.truetype(font_path, 56, index=1)
    lf = ImageFont.truetype(font_path, 34, index=1)
    sd.text((W / 2, 70), "크랑이 · 크랑이뉴스 동전 요정", font=tf, fill=INK, anchor="mm")
    cell = W / len(exprs)
    for i, (e, label) in enumerate(exprs):
        k = render_krangi(300, e)
        x = int(cell * i + (cell - k.width) / 2)
        sheet.paste(k, (x, 130), k)
        sd.text((cell * i + cell / 2, 500), label, font=lf, fill=GOLD_DARK, anchor="mm")
    sheet.save(out)
    print(out)
