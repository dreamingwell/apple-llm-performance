#!/usr/bin/env python3
"""What an M5 Ultra machine costs, per memory size the picker offers.

Prices are the cheapest Mac Apple sells with this chip at this memory, on the
smallest storage that configuration can be ordered with, so the figure tracks
the memory rather than an SSD upgrade. Read from the Apple Store's own product
data on the linked configurator URL on the date in `as_of`.
"""
ID = "m5ultra"
LABEL = "M5 Ultra"

_STUDIO = "https://www.apple.com/shop/buy-mac/mac-studio"

PRICES = {
    96: {
        "usd": 5499,
        "basis": "apple_new",
        "config": "Mac Studio, 30-core CPU / 64-core GPU, 96 GB, 1 TB SSD",
        "as_of": "2026-08-29",
        "source": ("Apple Store configurator",
                   f"{_STUDIO}/m5-ultra-chip-30-core-cpu-64-core-gpu-96gb-memory-1tb-storage"),
    },
    256: {
        "usd": 9499,
        "basis": "apple_new",
        "config": "Mac Studio, 30-core CPU / 64-core GPU, 256 GB, 1 TB SSD",
        "as_of": "2026-08-29",
        "note": "The 160 GB of memory over the base machine costs $4,000 on its own. "
                "The 36-core CPU / 80-core GPU part is a further $1,300 and buys no memory.",
        "source": ("Apple Store configurator",
                   f"{_STUDIO}/m5-ultra-chip-30-core-cpu-64-core-gpu-256gb-memory-1tb-storage"),
    },
}

UNPRICED = {
    512: "Apple has not published a price. The 512 GB Mac Studio was announced on "
         "25 August 2026 but cannot be ordered; Apple says late October.",
}
