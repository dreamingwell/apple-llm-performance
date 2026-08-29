#!/usr/bin/env python3
"""What an M3 machine costs, per memory size the picker offers.

Apple no longer sells this chip new, so these are Apple Certified
Refurbished prices - Apple's own list price for used hardware, read off the
linked product page. Same confidence class as a new list price and needing no
median or sample count, but the refurbished store stocks whatever Apple happens
to have refurbished and rotates constantly, so each entry is a snapshot: the
exact machine may be gone, and a different storage tier may be what is left.
"""
ID = "m3"
LABEL = "M3"

PRICES = {
    8: {
        "usd": 2119,
        "basis": "apple_refurb",
        "config": "24-inch iMac Apple M3 Chip with 8-Core CPU and 10-Core GPU - Blue, 2TB SSD",
        "as_of": "2026-08-29",
        "source": ("Apple Certified Refurbished", "https://www.apple.com/shop/product/g19l1ll/a/Refurbished-24-inch-iMac-Apple-M3-Chip-with-8-Core-CPU-and-10-Core-GPU-Blue"),
    },
    16: {
        "usd": 2289,
        "basis": "apple_refurb",
        "config": "24-inch iMac Apple M3 Chip with 8-Core CPU and 10-Core GPU - Pink, 2TB SSD",
        "as_of": "2026-08-29",
        "source": ("Apple Certified Refurbished", "https://www.apple.com/shop/product/g19n4ll/a/Refurbished-24-inch-iMac-Apple-M3-Chip-with-8-Core-CPU-and-10-Core-GPU-Pink"),
    },
}

UNPRICED = {
    24: "Apple does not sell this chip new, and no 24 GB machine was in the Certified Refurbished store on 2026-08-29.",
}
