#!/usr/bin/env python3
"""What an M4 Max machine costs, per memory size the picker offers.

Apple no longer sells this chip new, so these are Apple Certified
Refurbished prices - Apple's own list price for used hardware, read off the
linked product page. Same confidence class as a new list price and needing no
median or sample count, but the refurbished store stocks whatever Apple happens
to have refurbished and rotates constantly, so each entry is a snapshot: the
exact machine may be gone, and a different storage tier may be what is left.
"""
ID = "m4max"
LABEL = "M4 Max"

PRICES = {
    36: {
        "usd": 2969,
        "basis": "apple_refurb",
        "config": "14-inch MacBook Pro Apple M4 Max Chip with 14\u2011Core CPU and 32\u2011Core GPU - Space Black, 1TB SSD",
        "chassis": "laptop",
        "as_of": "2026-08-29",
        "source": ("Apple Certified Refurbished", "https://www.apple.com/shop/product/fx2k3ll/a/Refurbished-14-inch-MacBook-Pro-Apple-M4-Max-Chip-with-14%E2%80%91Core-CPU-and-32%E2%80%91Core-GPU-Space-Black"),
    },
    48: {
        "usd": 3899,
        "basis": "apple_refurb",
        "config": "14-inch MacBook Pro Apple M4 Max Chip with 16\u2011Core CPU and 40\u2011Core GPU - Space Black, 2TB SSD",
        "chassis": "laptop",
        "as_of": "2026-08-29",
        "source": ("Apple Certified Refurbished", "https://www.apple.com/shop/product/g1fg4ll/a/Refurbished-14-inch-MacBook-Pro-Apple-M4-Max-Chip-with-16%E2%80%91Core-CPU-and-40%E2%80%91Core-GPU-Space-Black"),
    },
}

UNPRICED = {
    64: "Apple does not sell this chip new, and no 64 GB machine was in the Certified Refurbished store on 2026-08-29.",
    128: "Apple does not sell this chip new, and no 128 GB machine was in the Certified Refurbished store on 2026-08-29.",
}
