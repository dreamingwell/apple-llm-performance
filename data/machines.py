"""Every M-series chip the picker offers, and what it can do.

Shared, not per-record: one small file rather than a record each, because the
list is short, closed and changes once a year. It used to live as a JavaScript
object literal inside tracker/render_status.py; it moved here when the decode
ceiling started needing `bw` on the Python side too, and two copies of a
bandwidth table is exactly the kind of thing that goes stale silently.

Fields:

  label    what the dropdown shows
  gen      groups the dropdown
  bw       peak unified-memory bandwidth in GB/s, from Apple's own specification.
           This is the theoretical peak, not an achieved figure - see
           tracker/throughput.py for what that distinction costs.
  mem      the union of unified-memory options across every Mac that shipped
           with this chip: laptops, mini, iMac, Studio and Mac Pro. The chip is
           what decides whether a model fits, not the case.
  tb/link  the Thunderbolt generation and its link rate in Gb/s
  tb5      Thunderbolt 5, which is what RDMA and JACCL tensor parallelism need;
           everything older pools only over the ring/pipeline path
  ports    Thunderbolt ports, which caps a full mesh
  bwNote   set where a binned variant of the same chip has lower bandwidth
"""

MACHINES = {
    "m1":      {"label": "M1",       "gen": "M1", "bw": 68,   "mem": [8, 16],
                "tb": "Thunderbolt 3 / USB4", "link": 40, "tb5": False, "ports": 2},
    "m1pro":   {"label": "M1 Pro",   "gen": "M1", "bw": 200,  "mem": [16, 32],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 3},
    "m1max":   {"label": "M1 Max",   "gen": "M1", "bw": 400,  "mem": [32, 64],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 4},
    "m1ultra": {"label": "M1 Ultra", "gen": "M1", "bw": 800,  "mem": [64, 128],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 6},
    "m2":      {"label": "M2",       "gen": "M2", "bw": 100,  "mem": [8, 16, 24],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 2},
    "m2pro":   {"label": "M2 Pro",   "gen": "M2", "bw": 200,  "mem": [16, 32],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 4},
    "m2max":   {"label": "M2 Max",   "gen": "M2", "bw": 400,  "mem": [32, 64, 96],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 4},
    "m2ultra": {"label": "M2 Ultra", "gen": "M2", "bw": 800,  "mem": [64, 128, 192],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 6},
    "m3":      {"label": "M3",       "gen": "M3", "bw": 100,  "mem": [8, 16, 24],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 2},
    "m3pro":   {"label": "M3 Pro",   "gen": "M3", "bw": 150,  "mem": [18, 36],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 3},
    "m3max":   {"label": "M3 Max",   "gen": "M3", "bw": 400,  "mem": [36, 48, 64, 96, 128],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 3,
                "bwNote": "300 GB/s on the binned 14-core CPU / 30-core GPU part"},
    "m3ultra": {"label": "M3 Ultra", "gen": "M3", "bw": 819,  "mem": [96, 256, 512],
                "tb": "Thunderbolt 5", "link": 80, "tb5": True, "ports": 6},
    "m4":      {"label": "M4",       "gen": "M4", "bw": 120,  "mem": [16, 24, 32],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 2},
    "m4pro":   {"label": "M4 Pro",   "gen": "M4", "bw": 273,  "mem": [24, 48, 64],
                "tb": "Thunderbolt 5", "link": 80, "tb5": True, "ports": 3},
    "m4max":   {"label": "M4 Max",   "gen": "M4", "bw": 546,  "mem": [36, 48, 64, 128],
                "tb": "Thunderbolt 5", "link": 80, "tb5": True, "ports": 4,
                "bwNote": "410 GB/s on the binned 14-core CPU part"},
    "m5":      {"label": "M5",       "gen": "M5", "bw": 153,  "mem": [16, 24, 32],
                "tb": "Thunderbolt 4", "link": 40, "tb5": False, "ports": 2},
    "m5pro":   {"label": "M5 Pro",   "gen": "M5", "bw": 307,  "mem": [24, 48, 64],
                "tb": "Thunderbolt 5", "link": 80, "tb5": True, "ports": 3},
    "m5max":   {"label": "M5 Max",   "gen": "M5", "bw": 614,  "mem": [36, 48, 64, 128],
                "tb": "Thunderbolt 5", "link": 80, "tb5": True, "ports": 4,
                "bwNote": "460 GB/s on the 32-core GPU part; 614 on the 40-core"},
    "m5ultra": {"label": "M5 Ultra", "gen": "M5", "bw": 1200, "mem": [96, 256, 512],
                "tb": "Thunderbolt 5", "link": 80, "tb5": True, "ports": 6},
}

# Newest first: the dropdown's optgroup order.
GENS = ["M5", "M4", "M3", "M2", "M1"]
