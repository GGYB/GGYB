from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont, ImageFilter


W, H = 1100, 300
FRAME_COUNT = 24

BG_TOP = (2, 6, 23)
BG_BOTTOM = (15, 23, 42)
GRID = (30, 41, 59)
TEXT_PRIMARY = (226, 232, 240)
TEXT_SECONDARY = (147, 197, 253)
TEXT_MUTED = (148, 163, 184)
CHIP_FILL = (17, 24, 39)
CHIP_BORDER = (51, 65, 85)
CHIP_TEXT = (203, 213, 225)

TITLE_X = 48
TITLE_Y = 92
TITLE_TEXT = "AlgoRondo"
CURSOR_GAP = 18

TITLE_FONT = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58
)
SUB_FONT = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 22
)
BODY_FONT = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 20
)
SMALL_FONT = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15
)


def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill)
    draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill)
    draw.pieslice((x1, y1, x1 + 2 * radius, y1 + 2 * radius), 180, 270, fill=fill)
    draw.pieslice((x2 - 2 * radius, y1, x2, y1 + 2 * radius), 270, 360, fill=fill)
    draw.pieslice((x1, y2 - 2 * radius, x1 + 2 * radius, y2), 90, 180, fill=fill)
    draw.pieslice((x2 - 2 * radius, y2 - 2 * radius, x2, y2), 0, 90, fill=fill)
    if outline:
        for off in range(width):
            draw.arc(
                (x1 + off, y1 + off, x1 + 2 * radius - off, y1 + 2 * radius - off),
                180,
                270,
                fill=outline,
            )
            draw.arc(
                (x2 - 2 * radius + off, y1 + off, x2 - off, y1 + 2 * radius - off),
                270,
                360,
                fill=outline,
            )
            draw.arc(
                (x1 + off, y2 - 2 * radius + off, x1 + 2 * radius - off, y2 - off),
                90,
                180,
                fill=outline,
            )
            draw.arc(
                (x2 - 2 * radius + off, y2 - 2 * radius + off, x2 - off, y2 - off),
                0,
                90,
                fill=outline,
            )
            draw.line((x1 + radius, y1 + off, x2 - radius, y1 + off), fill=outline)
            draw.line((x1 + radius, y2 - off, x2 - radius, y2 - off), fill=outline)
            draw.line((x1 + off, y1 + radius, x1 + off, y2 - radius), fill=outline)
            draw.line((x2 - off, y1 + radius, x2 - off, y2 - radius), fill=outline)


def lerp(a, b, t):
    return int(a + (b - a) * t)


def text_size(draw, text, font):
    if hasattr(draw, "textbbox"):
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        return right - left, bottom - top
    return draw.textsize(text, font=font)


def build_frame(frame_index):
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pixels = image.load()

    for y in range(H):
        t = y / max(H - 1, 1)
        color = tuple(lerp(BG_TOP[c], BG_BOTTOM[c], t) for c in range(3))
        for x in range(W):
            pixels[x, y] = color + (255,)

    draw = ImageDraw.Draw(image)

    for x in range(0, W, 28):
        draw.line((x, 0, x, H), fill=GRID, width=1)
    for y in range(0, H, 28):
        draw.line((0, y, W, y), fill=GRID, width=1)

    orb_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    orb_draw = ImageDraw.Draw(orb_layer)
    for cx, cy, r, color, phase_x, phase_y in [
        (900, 70, 70, (8, 47, 73, 140), 10, 7),
        (1000, 235, 98, (49, 46, 129, 130), -12, -8),
        (855, 225, 36, (20, 78, 74, 160), 0, -10),
    ]:
        ox = int(math.sin((frame_index / FRAME_COUNT) * 2 * math.pi) * phase_x)
        oy = int(math.cos((frame_index / FRAME_COUNT) * 2 * math.pi) * phase_y)
        orb_draw.ellipse((cx - r + ox, cy - r + oy, cx + r + ox, cy + r + oy), fill=color)
    orb_layer = orb_layer.filter(ImageFilter.GaussianBlur(6))
    image.alpha_composite(orb_layer)
    draw = ImageDraw.Draw(image)

    rounded_rect(draw, (48, 38, 240, 72), 17, fill=CHIP_FILL, outline=CHIP_BORDER, width=1)
    draw.text((66, 48), "GGYB / AlgoRondo", font=SMALL_FONT, fill=CHIP_TEXT)

    draw.text((TITLE_X, TITLE_Y), TITLE_TEXT, font=TITLE_FONT, fill=TEXT_PRIMARY)
    title_width, _ = text_size(draw, TITLE_TEXT, TITLE_FONT)
    cursor_x = TITLE_X + title_width + CURSOR_GAP
    if frame_index % 12 < 7:
        rounded_rect(draw, (cursor_x, 102, cursor_x + 12, 148), 3, fill=(96, 165, 250))

    draw.text(
        (48, 156),
        "algorithm engineer // geometry-minded // music-driven",
        font=SUB_FONT,
        fill=TEXT_SECONDARY,
    )
    draw.text((48, 208), "$ focus --current", font=BODY_FONT, fill=TEXT_MUTED)
    draw.text(
        (48, 238),
        "SLAM · Point Cloud · Integrated Navigation",
        font=BODY_FONT,
        fill=TEXT_PRIMARY,
    )
    draw.text(
        (48, 264), "Classical CV · C++ · LLM-curious", font=BODY_FONT, fill=TEXT_PRIMARY
    )

    points = []
    for step in range(0, 420, 8):
        x = 620 + step
        y = 188 + math.sin((step / 48.0) + frame_index * 0.26) * 32
        y += math.cos((step / 88.0) + frame_index * 0.18) * 10
        points.append((x, y))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.line(points, fill=(96, 165, 250, 150), width=12)
    glow = glow.filter(ImageFilter.GaussianBlur(7))
    image.alpha_composite(glow)
    draw = ImageDraw.Draw(image)

    for idx in range(len(points) - 1):
        t = (idx + frame_index) / len(points)
        if t < 0.33:
            color = (20, 184, 166)
        elif t < 0.66:
            color = (96, 165, 250)
        else:
            color = (167, 139, 250)
        draw.line((points[idx], points[idx + 1]), fill=color, width=6)

    head_idx = (frame_index * 3) % len(points)
    hx, hy = points[head_idx]
    for r, alpha in [(18, 70), (11, 170), (6, 255)]:
        draw.ellipse((hx - r, hy - r, hx + r, hy + r), fill=(96, 165, 250, alpha))

    base_x = 960
    for bar in range(5):
        amp = 8 + int((math.sin(frame_index * 0.35 + bar * 0.8) + 1) * 12)
        x0 = base_x + bar * 18
        rounded_rect(draw, (x0, 244 - amp, x0 + 10, 244 + amp), 4, fill=(20, 184, 166))

    return image


def main():
    frames = [build_frame(i) for i in range(FRAME_COUNT)]
    output = Path("assets/hero-banner-animated.gif")
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(output)


if __name__ == "__main__":
    main()
