"""
Synthetic (procedural) CT-style test image generator.

Generates a series of purely synthetic, high-resolution test images with a
"CT look" (grayscale, noise, soft tissue transitions, bone-like structures).
These are NOT real medical scans or real patient data - all values, IDs and
structures are made up and serve only as visual test material for the
gesture-/voice-controlled viewer.

Resolution: 2048x2048 px -> pixel-sharp on a MacBook Pro Retina display
(including fullscreen), since it's well above the native window size.
"""

import os
import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RES = 2048                     # edge length in pixels (square)
NUM_SLICES = 12                # number of slices in the series
target_dir = os.path.join("..", "assets", "ct")
os.makedirs(target_dir, exist_ok=True)

CENTER = (RES // 2, RES // 2)
rng = np.random.default_rng(42)  # fixed seed -> reproducible series


def add_ct_noise(img_f, base_sigma=6.0):
    """Adds Gaussian noise similar to what real CT raw images exhibit."""
    noise = rng.normal(0, base_sigma, img_f.shape).astype(np.float32)
    return img_f + noise


def soft_ellipse(img_f, center, axes, angle, value, blur_ksize=25, noise_sigma=3.0):
    """Draws an ellipse with a soft, textured transition instead of a hard edge."""
    mask = np.zeros(img_f.shape, dtype=np.float32)
    cv2.ellipse(mask, center, axes, angle, 0, 360, 1.0, -1)
    mask = cv2.GaussianBlur(mask, (blur_ksize, blur_ksize), 0)
    tissue_noise = rng.normal(0, noise_sigma, img_f.shape).astype(np.float32)
    img_f += mask * (value + tissue_noise - img_f) * 0.9
    return img_f


def draw_ribs(img_f, center_y, body_axes, slice_ratio):
    """Simulates rib/bone rings around the edge of the body cross-section (thorax slices)."""
    num_ribs = 10
    for k in range(num_ribs):
        t = k / (num_ribs - 1)
        angle = 200 + t * 140  # only lateral/anterior, not the spine side
        for side in (1, -1):
            a = np.radians(angle * side if side < 0 else angle)
            rx = body_axes[0] * 0.92
            ry = body_axes[1] * 0.92
            x = int(CENTER[0] + side * rx * np.cos(np.radians(t * 70 + 15)))
            y = int(center_y - ry * 0.5 + ry * 0.9 * t)
            cv2.ellipse(img_f, (x, y), (14, 6), 0, 0, 360, 950.0, -1)


def generate_slice(i, total):
    """
    Generates a single axial slice.
    i / total controls which body region is simulated:
      - beginning/end of the series: more thoracic (lungs, ribs)
      - middle: more abdominal (soft-tissue organs, spine)
    """
    ratio = i / max(total - 1, 1)  # 0.0 .. 1.0 across the series

    # Background: "air" outside the body (very dark, slightly noisy)
    img_f = np.full((RES, RES), 15.0, dtype=np.float32)

    body_axes = (int(RES * 0.34), int(RES * 0.27))
    body_center = (CENTER[0], int(RES * 0.48))

    # 1) Body contour: skin/fat layer -> muscle -> base soft-tissue tone
    img_f = soft_ellipse(img_f, body_center, body_axes, 0, 70, blur_ksize=41, noise_sigma=4)
    img_f = soft_ellipse(
        img_f, body_center,
        (int(body_axes[0] * 0.94), int(body_axes[1] * 0.94)), 0,
        95, blur_ksize=35, noise_sigma=5,
    )
    img_f = soft_ellipse(
        img_f, body_center,
        (int(body_axes[0] * 0.88), int(body_axes[1] * 0.88)), 0,
        120, blur_ksize=45, noise_sigma=6,
    )

    # 2) Region-specific internal structures
    if ratio < 0.35 or ratio > 0.85:
        # Thoracic region: two "lung wings" (dark, air-filled) + ribs
        lung_val = 40
        img_f = soft_ellipse(
            img_f, (body_center[0] - int(body_axes[0] * 0.45), body_center[1] - 10),
            (int(body_axes[0] * 0.36), int(body_axes[1] * 0.62)), 8,
            lung_val, blur_ksize=31, noise_sigma=8,
        )
        img_f = soft_ellipse(
            img_f, (body_center[0] + int(body_axes[0] * 0.45), body_center[1] - 10),
            (int(body_axes[0] * 0.36), int(body_axes[1] * 0.62)), -8,
            lung_val, blur_ksize=31, noise_sigma=8,
        )
        draw_ribs(img_f, body_center[1], body_axes, ratio)
        # Heart shadow, centered-left, slightly brighter than lung tissue
        img_f = soft_ellipse(
            img_f, (body_center[0] - int(body_axes[0] * 0.05), body_center[1] + int(body_axes[1] * 0.05)),
            (int(body_axes[0] * 0.22), int(body_axes[1] * 0.26)), 0,
            160, blur_ksize=29, noise_sigma=6,
        )
    else:
        # Abdominal region: liver, spleen, kidney-like structures
        img_f = soft_ellipse(
            img_f, (body_center[0] + int(body_axes[0] * 0.28), body_center[1] - int(body_axes[1] * 0.05)),
            (int(body_axes[0] * 0.42), int(body_axes[1] * 0.34)), -15,
            150, blur_ksize=33, noise_sigma=5,
        )  # liver
        img_f = soft_ellipse(
            img_f, (body_center[0] - int(body_axes[0] * 0.5), body_center[1] - int(body_axes[1] * 0.15)),
            (int(body_axes[0] * 0.2), int(body_axes[1] * 0.18)), 10,
            140, blur_ksize=27, noise_sigma=5,
        )  # spleen
        img_f = soft_ellipse(
            img_f, (body_center[0] - int(body_axes[0] * 0.35), body_center[1] + int(body_axes[1] * 0.35)),
            (int(body_axes[0] * 0.16), int(body_axes[1] * 0.22)), 0,
            130, blur_ksize=25, noise_sigma=5,
        )  # left kidney
        img_f = soft_ellipse(
            img_f, (body_center[0] + int(body_axes[0] * 0.35), body_center[1] + int(body_axes[1] * 0.35)),
            (int(body_axes[0] * 0.16), int(body_axes[1] * 0.22)), 0,
            130, blur_ksize=25, noise_sigma=5,
        )  # right kidney
        # Bowel loops: several small irregular ellipses
        for _ in range(6):
            ox = rng.integers(-int(body_axes[0] * 0.4), int(body_axes[0] * 0.4))
            oy = rng.integers(-int(body_axes[1] * 0.1), int(body_axes[1] * 0.55))
            ax1 = rng.integers(30, 70)
            ax2 = rng.integers(20, 45)
            ang = rng.integers(0, 180)
            val = rng.integers(95, 125)
            img_f = soft_ellipse(
                img_f, (body_center[0] + ox, body_center[1] + oy),
                (ax1, ax2), ang, float(val), blur_ksize=17, noise_sigma=6,
            )

    # 3) Spine (visible in almost every slice, bottom center)
    spine_y = body_center[1] + int(body_axes[1] * 0.78)
    cv2.circle(img_f, (CENTER[0], spine_y), int(RES * 0.045), (255,), -1)
    img_f = cv2.GaussianBlur(img_f, (9, 9), 0) if False else img_f  # placeholder no-op (structure stays sharp)
    cv2.circle(img_f, (CENTER[0], spine_y), int(RES * 0.032), (200,), -1)
    cv2.circle(img_f, (CENTER[0], spine_y), int(RES * 0.014), (10,), -1)  # spinal canal

    # 4) Global noise (detector/quantum noise), slightly smoothed for a "photon" look
    img_f = add_ct_noise(img_f, base_sigma=7.0)
    img_f = cv2.GaussianBlur(img_f, (3, 3), 0)

    # 5) Convert to 8-bit + light CLAHE for a "clinical" contrast look
    img_clamped = np.clip(img_f, 0, 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(16, 16))
    img_eq = clahe.apply(img_clamped)

    img_bgr = cv2.cvtColor(img_eq, cv2.COLOR_GRAY2BGR)

    # 6) Vignette (detector field gets slightly darker toward the edges)
    yy, xx = np.mgrid[0:RES, 0:RES]
    dist = np.sqrt((xx - CENTER[0]) ** 2 + (yy - CENTER[1]) ** 2) / (RES * 0.72)
    vignette = np.clip(1.0 - 0.35 * np.clip(dist - 0.55, 0, 1), 0.6, 1.0).astype(np.float32)
    img_bgr = (img_bgr.astype(np.float32) * vignette[..., None]).astype(np.uint8)

    # 7) Overlay: clinical style, position scaled relative to resolution
    s = RES / 512.0  # scale factor relative to reference resolution
    font = cv2.FONT_HERSHEY_SIMPLEX
    green = (0, 255, 0)
    cyan = (255, 255, 0)
    gray = (170, 170, 170)
    white = (255, 255, 255)

    def put(text, org, scale, color, thick=1):
        cv2.putText(img_bgr, text, (int(org[0] * s), int(org[1] * s)), font,
                    scale * s * 0.9, color, max(1, int(thick * s * 0.6)), cv2.LINE_AA)

    put("ID: TEST-ID-12345678", (20, 30), 0.5, green)
    put("SYNTHETIC_TEST_SUBJECT", (20, 50), 0.4, (200, 200, 200))
    put(f"SLICE: {i + 1}/{total}", (380, 30), 0.5, cyan)
    put("KV: 120 / MA: 240", (360, 50), 0.4, gray)
    put("R", (20, 262), 0.6, white)
    put("L", (480, 262), 0.6, white)
    put("AXIAL VIEW  |  SYNTHETIC TEST DATA", (20, 490), 0.4, gray)

    # subtle crosshair axes at the edges
    m = int(20 * s)
    ln = int(20 * s)
    cv2.line(img_bgr, (RES // 2, m), (RES // 2, m + ln), (100, 100, 100), max(1, int(s)))
    cv2.line(img_bgr, (RES // 2, RES - m - ln), (RES // 2, RES - m), (100, 100, 100), max(1, int(s)))
    cv2.line(img_bgr, (m, RES // 2), (m + ln, RES // 2), (100, 100, 100), max(1, int(s)))
    cv2.line(img_bgr, (RES - m - ln, RES // 2), (RES - m, RES // 2), (100, 100, 100), max(1, int(s)))

    return img_bgr


def main():
    for i in range(NUM_SLICES):
        img = generate_slice(i, NUM_SLICES)
        filename = os.path.join(target_dir, f"slice_{i + 1}.png")
        cv2.imwrite(filename, img)
        print(f"Synthetic CT test image generated: {filename}")

    print(f"\nDone! Generated {NUM_SLICES} slices at {RES}x{RES}px "
          f"(sharp on MacBook Pro Retina displays in fullscreen).")
    print("Note: purely synthetic, procedurally generated test material, not real scans.")


if __name__ == "__main__":
    main()