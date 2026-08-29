#!/usr/bin/env python3
"""What an M5 Pro machine costs, per memory size the picker offers.

Prices are the cheapest Mac Apple sells with this chip at this memory, on the
smallest storage that configuration can be ordered with, so the figure tracks
the memory rather than an SSD upgrade. Read from the Apple Store's own product
data on the linked configurator URL on the date in `as_of`.
"""
ID = "m5pro"
LABEL = "M5 Pro"

_MINI = "https://www.apple.com/shop/buy-mac/mac-mini"

PRICES = {
    24: {
        "usd": 1699,
        "basis": "apple_new",
        "config": "Mac mini, 15-core CPU / 16-core GPU, 24 GB, 512 GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "note": "The cheapest way onto this chip. Apple sells M5 Pro in the Mac mini "
                "and the MacBook Pro; the mini is the cheaper of the two and the only "
                "one you would rack.",
        "source": ("Apple Store configurator",
                   f"{_MINI}/m5-pro-chip-15-core-cpu-16-core-gpu-24gb-memory-512gb-storage"),
    },
    48: {
        "usd": 2299,
        "basis": "apple_new",
        "config": "Mac mini, 15-core CPU / 16-core GPU, 48 GB, 512 GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "source": ("Apple Store configurator",
                   f"{_MINI}/m5-pro-chip-15-core-cpu-16-core-gpu-48gb-memory-512gb-storage"),
    },
    64: {
        "usd": 2699,
        "basis": "apple_new",
        "config": "Mac mini, 15-core CPU / 16-core GPU, 64 GB, 512 GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "note": "$2,699 buys 64 GB behind 307 GB/s. The same 64 GB on an M5 Max is "
                "$3,499 and doubles the bandwidth, which is what decides tokens per "
                "second once a model fits.",
        "source": ("Apple Store configurator",
                   f"{_MINI}/m5-pro-chip-15-core-cpu-16-core-gpu-64gb-memory-512gb-storage"),
    },
}
