#!/usr/bin/env python3
"""What a base M5 machine costs, per memory size the picker offers.

Prices are the cheapest Mac Apple sells with this chip at this memory, on the
smallest storage that configuration can be ordered with, so the figure tracks
the memory rather than an SSD upgrade. Read from the Apple Store's own product
data on the linked configurator URL on the date in `as_of`.
"""
ID = "m5"
LABEL = "M5"

_AIR = "https://www.apple.com/shop/buy-mac/macbook-air"
_GPU_TIED = ("On the 13-inch Air, anything above 16 GB comes with the 10-core GPU part; "
             "Apple does not sell the memory on its own.")

PRICES = {
    16: {
        "usd": 1299,
        "basis": "apple_new",
        "config": "MacBook Air 13-inch, 10-core CPU / 8-core GPU, 16 GB, 512 GB SSD",
        "as_of": "2026-08-29",
        "note": "The Mac mini no longer ships a plain M5 - it starts at M6 - so the "
                "cheapest M5 is a laptop.",
        "source": ("Apple Store configurator",
                   f"{_AIR}/13-inch-silver-m5-chip-10-core-cpu-8-core-gpu-16gb-memory-512gb-storage"),
    },
    24: {
        "usd": 1499,
        "basis": "apple_new",
        "config": "MacBook Air 13-inch, 10-core CPU / 10-core GPU, 24 GB, 512 GB SSD",
        "as_of": "2026-08-29",
        "note": _GPU_TIED,
        "source": ("Apple Store configurator",
                   f"{_AIR}/13-inch-silver-m5-chip-10-core-cpu-10-core-gpu-24gb-memory-512gb-storage"),
    },
    32: {
        "usd": 1699,
        "basis": "apple_new",
        "config": "MacBook Air 13-inch, 10-core CPU / 10-core GPU, 32 GB, 512 GB SSD",
        "as_of": "2026-08-29",
        "note": _GPU_TIED,
        "source": ("Apple Store configurator",
                   f"{_AIR}/13-inch-silver-m5-chip-10-core-cpu-10-core-gpu-32gb-memory-512gb-storage"),
    },
}
