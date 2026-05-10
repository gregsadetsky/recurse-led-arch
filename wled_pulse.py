# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Cycle WLED through the hue wheel via the JSON API.

Index 0 is the onboard RGBW indicator (different bus); the 192-LED main
strip is at indices 1..192. Default lights the whole main strip.
Use --pixel N to light only one LED, or --start/--stop for a range.
"""

import argparse
import colorsys
import json
import time
import urllib.request

WLED = "http://10.100.3.132/json/state"
BRI = 255  # 0..255 — edit here, or override with --bri


def post(body: dict) -> None:
    req = urllib.request.Request(
        WLED,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=2).read()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pixel", type=int, help="light only this LED index")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--stop", type=int, default=193, help="exclusive")
    p.add_argument("--bri", type=int, default=BRI, help="0..255")
    p.add_argument("--hz", type=float, default=100.0)
    args = p.parse_args()

    start, stop = (args.pixel, args.pixel + 1) if args.pixel is not None else (args.start, args.stop)

    post({
        "on": True,
        "bri": args.bri,
        "transition": 0,
        "seg": [
            {"id": 0, "start": start, "stop": stop, "fx": 0, "col": [[255, 0, 0]]},
            {"id": 1, "stop": 0},
        ],
    })
    print(f"lit segment: [{start}, {stop}) — {stop - start} LED(s)")

    period = 1.0 / args.hz
    t0 = time.monotonic()
    while True:
        t = time.monotonic() - t0
        hue = t * 0.1 % 1.0
        r, g, b = (int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1.0, 1.0))
        bri = args.bri  # vary here for breathing, e.g. int(args.bri * (0.5 + 0.5 * math.sin(t)))
        post({"bri": bri, "seg": [{"id": 0, "col": [[r, g, b]]}]})
        time.sleep(period)


if __name__ == "__main__":
    main()
