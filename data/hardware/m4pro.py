#!/usr/bin/env python3
"""What an M4 Pro machine costs, per memory size the picker offers.

Apple no longer sells this chip new, so these are Apple Certified
Refurbished prices - Apple's own list price for used hardware, read off the
linked product page. Same confidence class as a new list price and needing no
median or sample count, but the refurbished store stocks whatever Apple happens
to have refurbished and rotates constantly, so each entry is a snapshot: the
exact machine may be gone, and a different storage tier may be what is left.
"""
ID = "m4pro"
LABEL = "M4 Pro"

PRICES = {
    24: {
        "usd": 1779,
        "basis": "apple_refurb",
        "config": "14-inch MacBook Pro Apple M4 Pro Chip with 12\u2011Core CPU and 16\u2011Core GPU - Silver, 512GB SSD",
        "chassis": "laptop",
        "as_of": "2026-08-29",
        "source": ("Apple Certified Refurbished", "https://www.apple.com/shop/product/fx2e3ll/a/Refurbished-14-inch-MacBook-Pro-Apple-M4-Pro-Chip-with-12%E2%80%91Core-CPU-and-16%E2%80%91Core-GPU-Silver"),
    },
}

UNPRICED = {
    48: "Apple does not sell this chip new, and no 48 GB machine was in the Certified Refurbished store on 2026-08-29.",
    64: "Apple does not sell this chip new, and no 64 GB machine was in the Certified Refurbished store on 2026-08-29.",
}
