#!/usr/bin/env python3
"""What an M5 Max machine costs, per memory size the picker offers.

Prices are the cheapest Mac Apple sells with this chip at this memory, on the
smallest storage that configuration can be ordered with, so the figure tracks
the memory rather than an SSD upgrade. Read from the Apple Store's own product
data on the linked configurator URL on the date in `as_of`.
"""
ID = "m5max"
LABEL = "M5 Max"

_STUDIO = "https://www.apple.com/shop/buy-mac/mac-studio"
_TIED = ("Anything above 36 GB is only offered on the 40-core GPU part, so the first "
         "memory step carries a $300 GPU upgrade with it whether or not you want it.")

PRICES = {
    36: {
        "usd": 2499,
        "basis": "apple_new",
        "config": "Mac Studio, 18-core CPU / 32-core GPU, 36 GB, 512 GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "source": ("Apple Store configurator",
                   f"{_STUDIO}/m5-max-chip-18-core-cpu-32-core-gpu-36gb-memory-512gb-storage"),
    },
    48: {
        "usd": 3099,
        "basis": "apple_new",
        "config": "Mac Studio, 18-core CPU / 40-core GPU, 48 GB, 512 GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "note": _TIED,
        "source": ("Apple Store configurator",
                   f"{_STUDIO}/m5-max-chip-18-core-cpu-40-core-gpu-48gb-memory-512gb-storage"),
    },
    64: {
        "usd": 3499,
        "basis": "apple_new",
        "config": "Mac Studio, 18-core CPU / 40-core GPU, 64 GB, 512 GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "note": _TIED,
        "source": ("Apple Store configurator",
                   f"{_STUDIO}/m5-max-chip-18-core-cpu-40-core-gpu-64gb-memory-512gb-storage"),
    },
    128: {
        "usd": 5099,
        "basis": "apple_new",
        "config": "Mac Studio, 18-core CPU / 40-core GPU, 128 GB, 512 GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "note": "The step from 64 GB to 128 GB is $1,600, which is more than the base "
                "machine's entire memory upgrade path below it.",
        "source": ("Apple Store configurator",
                   f"{_STUDIO}/m5-max-chip-18-core-cpu-40-core-gpu-128gb-memory-512gb-storage"),
    },
}
