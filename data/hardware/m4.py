#!/usr/bin/env python3
"""What an M4 machine costs, per memory size the picker offers.

Apple no longer sells this chip new, so these are Apple Certified
Refurbished prices - Apple's own list price for used hardware, read off the
linked product page. Same confidence class as a new list price and needing no
median or sample count, but the refurbished store stocks whatever Apple happens
to have refurbished and rotates constantly, so each entry is a snapshot: the
exact machine may be gone, and a different storage tier may be what is left.
"""
ID = "m4"
LABEL = "M4"

PRICES = {
    16: {
        "usd": 1269,
        "basis": "apple_refurb",
        "config": "24-inch iMac Apple M4 Chip with 8-Core CPU and 8-Core GPU - Silver, 256GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "source": ("Apple Certified Refurbished", "https://www.apple.com/shop/product/fwuc3ll/a/Refurbished-24-inch-iMac-Apple-M4-Chip-with-8-Core-CPU-and-8-Core-GPU-Silver"),
    },
    24: {
        "usd": 1439,
        "basis": "apple_refurb",
        "config": "24-inch iMac Apple M4 Chip with 8-Core CPU and 8-Core GPU - Blue, 256GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "source": ("Apple Certified Refurbished", "https://www.apple.com/shop/product/g1e53ll/a/Refurbished-24-inch-iMac-Apple-M4-Chip-with-8-Core-CPU-and-8-Core-GPU-Blue"),
    },
    32: {
        "usd": 1949,
        "basis": "apple_refurb",
        "config": "24-inch iMac Apple M4 Chip with 10-Core CPU and 10-Core GPU, Gigabit Ethernet- Silver, 512GB SSD",
        "chassis": "desktop",
        "as_of": "2026-08-29",
        "source": ("Apple Certified Refurbished", "https://www.apple.com/shop/product/g1k14ll/a/refurbished-24-inch-imac-apple-m4-chip-with-10-core-cpu-and-10-core-gpu-gigabit-ethernet-silver"),
    },
}
