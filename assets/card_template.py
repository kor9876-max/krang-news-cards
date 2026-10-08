"""크랑이뉴스 카드 템플릿 (1080x1350, 인스타 4:5).

    from card_template import cover_card, article_card
    cover_card("10월 9일 (목)", ["헤드라인1", ...]).save("01.png")
    article_card(1, "경제", "제목", "본문 두세 문장", "생활 영향 한 줄",
                 krangi_says="크랑이 한마디", expr="happy").save("02.png")
expr: basic, happy, surprised, worried, wink
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from krangi import render_krangi, INK, GOLD, GOLD_DARK  # noqa: E402

W, H = 1080, 1350
BG = (255, 249, 236)
NAVY = (34, 40, 74)
ECON = (232, 120, 40)
POLI = (58, 104, 196)
LIFE_BG = (255, 233, 176)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def f(size, bold=True):
    return ImageFont.truetype(FONT if bold else FONT_R, size, index=1)


def wrap(d, text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        t = cur + ch
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            # 단어 중간에서 끊기지 않게 마지막 공백 기준으로 넘김
            sp = cur.rfind(" ")
            if sp > 0 and len(cur) - sp < 8:
                lines.append(cur[:sp])
                cur = cur[sp + 1:] + ch
            else:
                lines.append(cur)
                cur = ch
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, font, x, y, fill, gap=1.45):
    lh = int(font.size * gap)
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def bubble(img, box, text, font, tail_to):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=36, fill=(255, 255, 255), outline=INK, width=5)
    tx, ty = tail_to
    if tx < x0:  # 왼쪽 꼬리
        by = min(max(ty, y0 + 50), y1 - 50)
        d.polygon([(x0 + 3, by - 24), (x0 + 3, by + 24), (tx, ty)], fill=(255, 255, 255))
        d.line([(x0, by - 24), (tx, ty), (x0, by + 24)], fill=INK, width=5, joint="curve")
    else:  # 아래 꼬리
        bx = min(max(tx, x0 + 60), x1 - 60)
        d.polygon([(bx - 28, y1 - 3), (bx + 28, y1 - 3), (tx, ty)], fill=(255, 255, 255))
        d.line([(bx - 28, y1), (tx, ty), (bx + 28, y1)], fill=INK, width=5, joint="curve")
    lines = wrap(d, text, font, x1 - x0 - 70)
    lh = int(font.size * 1.4)
    yy = y0 + (y1 - y0 - lh * len(lines)) // 2 + 2
    for ln in lines:
        d.text(((x0 + x1) // 2, yy), ln, font=font, fill=INK, anchor="ma")
        yy += lh


def header(d, right_text):
    d.rectangle([0, 0, W, 110], fill=NAVY)
    d.text((60, 55), "크랑이뉴스", font=f(44), fill=GOLD, anchor="lm")
    d.text((W - 60, 55), right_text, font=f(32, False), fill=(220, 224, 240), anchor="rm")


def footer(d):
    d.text((W // 2, H - 48), "출처: 한국경제 · @krang_news", font=f(26, False), fill=(150, 130, 100), anchor="mm")


def cover_card(date_label, headlines, krangi_says="오늘 아침 주머니 사정, 크랑이가 챙겨왔어요!"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(d, date_label)
    d.text((60, 175), "아침 경제 브리핑", font=f(76), fill=INK)
    d.text((62, 285), "오늘 꼭 알아야 할 뉴스 5", font=f(40, False), fill=GOLD_DARK)

    y = 380
    nf = f(36)
    for i, h in enumerate(headlines[:5], 1):
        d.ellipse([60, y, 116, y + 56], fill=GOLD)
        d.text((88, y + 28), str(i), font=f(32), fill=INK, anchor="mm")
        lines = wrap(d, h, nf, W - 200)[:2]
        y2 = draw_lines(d, lines, nf, 140, y + 2, INK, gap=1.3)
        y = max(y + 80, y2 + 28)

    k = render_krangi(330, "happy")
    kx, ky = W - k.width - 40, H - k.height - 80
    img.paste(k, (kx, ky), k)
    bubble(img, (60, ky + 40, kx + 10, ky + 210), krangi_says, f(34), (kx + 40, ky + 250))
    footer(d)
    return img


def article_card(idx, category, title, body, life, krangi_says=None, expr="basic"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    header(d, f"{idx} / 5")
    col = ECON if category == "경제" else POLI
    d.rounded_rectangle([60, 150, 60 + 40 + d.textlength(category, font=f(32)), 206], radius=28, fill=col)
    d.text((80, 178), category, font=f(32), fill=(255, 255, 255), anchor="lm")

    y = draw_lines(d, wrap(d, title, f(58), W - 120)[:3], f(58), 60, 235, INK, gap=1.3)
    y += 25
    d.line([(60, y), (W - 60, y)], fill=(230, 214, 180), width=4)
    y += 35
    y = draw_lines(d, wrap(d, body, f(38, False), W - 120)[:6], f(38, False), 60, y, (60, 52, 40), gap=1.55)

    # 생활 영향 띠
    lf = f(38)
    life_lines = wrap(d, life, lf, W - 200)[:2]
    band_h = 90 + len(life_lines) * 54
    k = render_krangi(300, expr)
    band_y = H - 110 - k.height - band_h - 20
    band_y = max(band_y, y + 30)
    d.rounded_rectangle([60, band_y, W - 60, band_y + band_h], radius=28, fill=LIFE_BG)
    d.ellipse([95, band_y + 30, 133, band_y + 68], fill=GOLD, outline=GOLD_DARK, width=3)
    d.text((114, band_y + 49), "!", font=f(28), fill=INK, anchor="mm")
    d.text((148, band_y + 49), "내 생활엔?", font=f(32), fill=GOLD_DARK, anchor="lm")
    draw_lines(d, life_lines, lf, 95, band_y + 76, INK, gap=1.4)

    # 크랑이 + 말풍선
    kx, ky = 50, H - k.height - 70
    img.paste(k, (kx, ky), k)
    if krangi_says:
        bubble(img, (kx + k.width + 30, ky + 60, W - 60, ky + 230), krangi_says, f(36), (kx + k.width - 15, ky + 175))
    footer(d)
    return img


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    cover_card("샘플 · 10월 9일", [
        "[샘플] 기준금리 동결, 연말 인하 가능성 열어둬",
        "[샘플] 반도체 수출 석 달 연속 증가",
        "[샘플] 전세대출 한도 축소 검토",
        "[샘플] 국회, 내년도 예산안 심사 착수",
        "[샘플] 청년 월세 지원 신청 기간 연장",
    ]).save(os.path.join(out, "sample_01_cover.png"))
    article_card(
        1, "경제",
        "[샘플] 기준금리 동결… 연말 인하 가능성은 열어둬",
        "이 카드는 디자인 확인용 예시 문장이에요. 실제 기사 내용이 아니에요. "
        "실제 카드에서는 이 자리에 기사 핵심을 두세 문장으로 직접 요약해서 넣어요.",
        "변동금리 대출이라면 당장 이자는 그대로, 연말 인하 여부를 지켜보세요",
        krangi_says="대출 이자 당장은 그대로예요! 연말을 노려봐요",
        expr="wink",
    ).save(os.path.join(out, "sample_02_article.png"))
    print("done")
