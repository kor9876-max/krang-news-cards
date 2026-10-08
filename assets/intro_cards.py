"""크랑이뉴스 소개 카드 3장 (고정 게시물용, 1080x1350).

    python3 intro_cards.py <출력폴더>
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from card_template import W, H, BG, NAVY, LIFE_BG, ECON, POLI, f, bubble, header  # noqa: E402


def footer(d):
    d.text((W // 2, H - 48), "@krang_news", font=f(28, False), fill=(150, 130, 100), anchor="mm")
from krangi import render_krangi, INK, GOLD, GOLD_DARK  # noqa: E402


def card1():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(d, "소개 1 / 3")
    k = render_krangi(560, "happy")
    img.paste(k, ((W - k.width) // 2, 330), k)
    bubble(img, (140, 150, W - 140, 300), "안녕하세요! 저는 크랑이예요", f(46), (W // 2, 360))
    d.text((W // 2, 1040), "호랑이 + 동전 \"크랑~\"", font=f(40, False), fill=GOLD_DARK, anchor="mm")
    d.text((W // 2, 1120), "경제 뉴스를 쉽게 풀어주는", font=f(52), fill=INK, anchor="mm")
    d.text((W // 2, 1195), "동전 요정이에요", font=f(52), fill=INK, anchor="mm")
    footer(d)
    return img


def card2():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(d, "소개 2 / 3")
    d.text((60, 170), "매일 이렇게 찾아가요", font=f(64), fill=INK)
    rows = [
        (GOLD, "평일 아침 7시", "출근길에 딱 1분이면 끝나요"),
        (ECON, "경제 3개 + 정치 2개", "어제 꼭 알아야 할 뉴스만 골라요"),
        (LIFE_BG, "\"내 생활엔?\" 한 줄", "대출·물가·월급에 뭐가 바뀌는지"),
        (POLI, "카드 + 릴스", "천천히 읽거나, 24초로 훑거나"),
    ]
    y = 300
    for col, title, sub in rows:
        d.rounded_rectangle([60, y, W - 60, y + 160], radius=28, fill=(255, 255, 255), outline=(235, 220, 190), width=3)
        d.rounded_rectangle([60, y, 84, y + 160], radius=12, fill=col)
        d.text((115, y + 50), title, font=f(46), fill=INK, anchor="lm")
        d.text((115, y + 112), sub, font=f(34, False), fill=(110, 95, 70), anchor="lm")
        y += 185
    k = render_krangi(220, "wink")
    img.paste(k, (W - k.width - 40, H - k.height - 70), k)
    footer(d)
    return img


def card3():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(d, "소개 3 / 3")
    d.text((60, 170), "크랑이 표정을 보면", font=f(60), fill=INK)
    d.text((60, 250), "뉴스 분위기가 보여요", font=f(60), fill=INK)
    items = [("happy", "좋은 소식"), ("worried", "걱정 뉴스"), ("surprised", "깜짝 뉴스"), ("wink", "생활 꿀팁")]
    cw = (W - 120) // 4
    for i, (e, lab) in enumerate(items):
        k = render_krangi(230, e)
        x = 60 + cw * i + (cw - k.width) // 2
        img.paste(k, (x, 380), k)
        d.text((60 + cw * i + cw // 2, 690), lab, font=f(34), fill=GOLD_DARK, anchor="mm")
    d.rounded_rectangle([60, 790, W - 60, 1150], radius=36, fill=NAVY)
    d.text((W // 2, 880), "팔로우하고", font=f(50), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 960), "매일 아침 크랑이 만나기", font=f(56), fill=GOLD, anchor="mm")
    d.text((W // 2, 1060), "도움 된 카드는 저장해두세요!", font=f(36, False), fill=(220, 224, 240), anchor="mm")
    footer(d)
    return img


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    for i, fn in enumerate((card1, card2, card3), 1):
        fn().save(os.path.join(out, f"intro_{i:02d}.png"))
    print("done")
