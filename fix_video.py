"""
JARRAR AI video fixer — corrected coordinates.
Fixes:
  1. Larger "PREDICTION INTELLIGENCE BASIS" heading + bullets
  2. Bullets aligned to fixed column (no drift)
  3. Panel box width fits content (tighter)
  4. Subtitles moved to very bottom
"""

from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

VIDEO_IN  = "/root/.claude/uploads/27557df3-3375-5514-80f8-af35a4e4ddd7/872544b9-JARRAR_Loophole_Scenario_v5_final.mp4"
VIDEO_OUT = "/home/user/projects/JARRAR_Loophole_Scenario_v6_fixed.mp4"

W, H = 1920, 1080

# ── ACTUAL PANEL COORDS (verified by pixel scanning) ─────────────────────────
# Header spans y=98-155, text at y=117-131, x starts ~36, ends ~422
PANEL_X1      = 36
PANEL_Y1      = 98     # top of panel box
PANEL_X2      = 425    # right edge of original panel (to cover fully)

# y-centres of each bullet item text row (verified from pixel scan)
ITEM_Y_DETECT = [193, 227, 261, 295, 329, 363, 397, 431, 465, 499]
DETECT_X      = 200    # x to sample for item brightness

# Full panel height when all 10 items visible
PANEL_FULL_Y2 = 520

# Header detection: red fill at y=152, x=200
HDR_DETECT_Y  = 152
HDR_DETECT_X  = 200

# ── SUBTITLE COORDS (verified) ────────────────────────────────────────────────
SUB_Y1     = 882
SUB_Y2     = 958
SUB_H      = SUB_Y2 - SUB_Y1       # ≈ 76 px

FOOTER_H   = 22
SUB_NEW_Y1 = H - FOOTER_H - SUB_H  # ≈ 980
SUB_NEW_Y2 = H - FOOTER_H           # ≈ 1058

# ── ITEMS ─────────────────────────────────────────────────────────────────────
ITEMS = [
    "CHECKPOST VISIBILITY GAPS",
    "OLD INFILTRATION POINTS",
    "HILL SLOPE ANALYSIS",
    "VEGETATION & VACANT SPACES",
    "HILL SHADE ANALYSIS",
    "VIEWSHED ANALYSIS",
    "NATURAL COVER / CROPLAND",
    "PROXIMITY TO SETTLEMENTS",
    "SOCIAL MEDIA INTELLIGENCE",
    "CONSTRUCTION CHANGES",
]

# ── COLORS ────────────────────────────────────────────────────────────────────
C_DARK_BG   = (4,   9,  22)
C_PANEL_BG  = (5,  11,  28)
C_HDR_BG    = (148, 26,  26)
C_RED_DOT   = (255,  60,  60)
C_ORANGE    = (240, 162,  50)
C_WHITE     = (255, 255, 255)
C_ITEM_TXT  = (200, 220, 255)
C_BORDER    = (210,  45,  45)   # bright red border, matches header

# ── FONTS ─────────────────────────────────────────────────────────────────────
F_HDR_PATH  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
F_REG_PATH  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

F_HDR       = ImageFont.truetype(F_HDR_PATH, 18)   # "PREDICTED INFILTRATION POINTS"
F_SUB       = ImageFont.truetype(F_HDR_PATH, 14)   # "PREDICTION INTELLIGENCE BASIS"
F_ITEM      = ImageFont.truetype(F_REG_PATH, 13)   # bullet items

# ── LAYOUT CONSTANTS ─────────────────────────────────────────────────────────
PX          = 14     # horizontal padding inside box
BULLET_OFF  = PX            # bullet x offset from panel left
TEXT_OFF    = PX + 14       # text x offset (bullet column=10px + 4px gap)

HDR_H       = 36     # pixel height of red header
SUBH_H      = 22     # subheading row height
SEP         = 4      # gap after separator line
ITEM_H      = 24     # pixel height per bullet row
BODY_PT     = 8      # body padding top
BODY_PB     = 10     # body padding bottom

def _tw(text, font):
    tmp = Image.new("RGB", (1, 1))
    bb  = ImageDraw.Draw(tmp).textbbox((0,0), text, font=font)
    return bb[2] - bb[0]

# Compute box width from content
hdr_tw   = _tw("PREDICTED INFILTRATION POINTS", F_HDR)
sub_tw   = _tw("PREDICTION INTELLIGENCE BASIS", F_SUB)
max_i_tw = max(_tw(t, F_ITEM) for t in ITEMS)

BOX_W = max(
    14 + 12 + 8 + hdr_tw + PX,   # dot(12) + gap(8) + text + right-pad
    PX + sub_tw + PX,
    TEXT_OFF + max_i_tw + PX
) + 2   # +2 for border

def panel_h(n):
    body = BODY_PT + SUBH_H + SEP + ITEM_H * n + BODY_PB
    return HDR_H + (body if n > 0 else 0)

# ── PRE-RENDER PANEL STATES 0-10 ─────────────────────────────────────────────
def render_state(n):
    ph     = panel_h(n)
    canvas = Image.new("RGBA", (BOX_W + 2, ph + 2), (0,0,0,0))
    draw   = ImageDraw.Draw(canvas)
    bx, by = 1, 1

    # outer border — 2px thick red so panel body is clearly in the red box
    draw.rectangle([0, 0, BOX_W+3, ph+3], outline=(*C_BORDER, 255), width=2)

    # red header
    draw.rectangle([bx, by, bx+BOX_W, by+HDR_H], fill=(*C_HDR_BG, 230))
    # dot
    dy = by + HDR_H // 2
    draw.ellipse([bx+PX, dy-6, bx+PX+12, dy+6], fill=(*C_RED_DOT,255))
    # header text
    draw.text((bx+PX+18, by+HDR_H//2-9),
              "PREDICTED INFILTRATION POINTS", font=F_HDR, fill=(*C_WHITE,255))

    if n == 0:
        return canvas

    # body
    by2 = by + HDR_H
    bh  = panel_h(n) - HDR_H
    draw.rectangle([bx, by2, bx+BOX_W, by2+bh], fill=(*C_PANEL_BG, 230))

    # subheading
    sy = by2 + BODY_PT
    draw.text((bx+PX, sy), "PREDICTION INTELLIGENCE BASIS",
              font=F_SUB, fill=(*C_ORANGE, 255))

    # separator
    sep_y = sy + SUBH_H
    draw.line([(bx+PX, sep_y), (bx+BOX_W-PX, sep_y)], fill=(*C_ORANGE, 70))

    # bullet items — fixed columns, always aligned
    iy0 = sep_y + SEP
    for i, item in enumerate(ITEMS[:n]):
        row_y = iy0 + i * ITEM_H
        draw.text((bx+BULLET_OFF, row_y), "•",   font=F_ITEM, fill=(*C_ORANGE, 255))
        draw.text((bx+TEXT_OFF,   row_y), item,  font=F_ITEM, fill=(*C_ITEM_TXT, 255))

    return canvas

print("Pre-rendering 11 panel states …")
STATES = [render_state(n) for n in range(11)]
print(f"Done. Box width = {BOX_W}px (original was ~389px)")

# ── PRE-LOAD MAP REFERENCE ────────────────────────────────────────────────────
# Grab a frame before the panel appears (t=5s) so we have clean map pixels to
# restore below the new (shorter) panel box instead of leaving a dark rectangle.
print("Loading map reference frame …")
_ref_clip = VideoFileClip(VIDEO_IN)
MAP_REF   = _ref_clip.get_frame(5).copy()   # uint8 RGB, no panel present yet
_ref_clip.close()
print("Map reference loaded.")

# ── DETECTION ────────────────────────────────────────────────────────────────

def panel_visible(arr):
    r, g, b = arr[HDR_DETECT_Y, HDR_DETECT_X, :3]
    return int(r) > 150 and int(g) < 120 and int(b) < 120

def count_items(arr):
    """Count visible items by scanning for white text pixels (not blue circles)."""
    n = 0
    for y in ITEM_Y_DETECT:
        region = arr[y-2:y+2, 74:220, :]
        white = int(np.sum(
            (region[:,:,0]>190) & (region[:,:,1]>190) & (region[:,:,2]>190)
        ))
        if white > 15:
            n += 1
        else:
            break   # items appear top-to-bottom; first blank = none after
    return n

def sub_visible(arr):
    region = arr[SUB_Y1:SUB_Y2, 200:1720, :3]
    return bool(np.max(region) > 190 and np.mean(region) > 10)

# ── FRAME PROCESSOR ──────────────────────────────────────────────────────────

def process_frame(frame_arr):
    out = frame_arr.copy()

    # ── Subtitle: move to bottom ─────────────────────────────────────────────
    if sub_visible(out):
        sub_strip = out[SUB_Y1:SUB_Y2].copy()

        # Fill original position with a vertical gradient between the terrain
        # rows immediately above and below the subtitle band — this blends
        # naturally into the surrounding map instead of leaving a flat smear.
        top = out[SUB_Y1 - 3, :, :].astype(np.float32)
        bot = out[SUB_Y2 + 3, :, :].astype(np.float32)
        for i in range(SUB_H):
            alpha = i / (SUB_H - 1)
            out[SUB_Y1 + i] = (top * (1 - alpha) + bot * alpha).clip(0, 255).astype(np.uint8)

        # Paste at very bottom (above footer)
        out[SUB_NEW_Y1:SUB_NEW_Y2] = sub_strip

    # ── Panel: cover old, draw new ───────────────────────────────────────────
    if panel_visible(out):
        n = count_items(out)
        ph = panel_h(n)

        # How far down the ORIGINAL panel content extends (34px item spacing)
        orig_bottom = PANEL_Y1 + 57 + 28 + n * 34 + 20
        cover_y2    = max(PANEL_Y1 + ph + 5, orig_bottom)

        # 1. Restore the whole cover band from the clean map reference so there
        #    is no dark rectangle anywhere — new panel will be composited on top.
        out[PANEL_Y1-2 : cover_y2,
            PANEL_X1-2 : PANEL_X2 + 5] = MAP_REF[PANEL_Y1-2 : cover_y2,
                                                   PANEL_X1-2 : PANEL_X2 + 5]

        # 2. Composite new panel over the restored map pixels
        pw, phl = STATES[n].size
        region  = Image.fromarray(
            out[PANEL_Y1-1 : PANEL_Y1-1+phl,
                PANEL_X1-1 : PANEL_X1-1+pw]).convert("RGBA")
        region.alpha_composite(STATES[n])
        out[PANEL_Y1-1 : PANEL_Y1-1+phl,
            PANEL_X1-1 : PANEL_X1-1+pw] = np.array(region.convert("RGB"))

    return out

# ── RUN ───────────────────────────────────────────────────────────────────────
print("Opening source video …")
clip = VideoFileClip(VIDEO_IN)

print(f"Processing {clip.duration:.0f}s at {clip.fps}fps …")
out_clip = clip.image_transform(process_frame)

print(f"Encoding → {VIDEO_OUT}")
out_clip.write_videofile(
    VIDEO_OUT,
    codec="libx264",
    audio_codec="aac",
    fps=clip.fps,
    preset="fast",
    ffmpeg_params=["-crf", "20"],
    logger="bar"
)
clip.close()
print("Done.")
