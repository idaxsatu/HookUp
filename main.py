#!/usr/bin/env python3
"""
HookUp — CLI and helpers for AmstaMatchaXXX (Amsterdam tour guide, adult industry, optional messaging).
Venues, slots, bookings, messages. Single-file app.
Usage:
  python HookUp_app.py config | version | constants
  python HookUp_app.py venues list | add --curator 0x... --venue-id v1 --name "Canal House" --type CANAL_HOUSE
  python HookUp_app.py slots list --venue-id v1 | add --curator 0x... --slot-id s1 --venue-id v1 --start EPOCH --end EPOCH
  python HookUp_app.py book --guest 0x... --slot-id s1 --amount-wei 1000000
  python HookUp_app.py message --from 0x... --to 0x... --content-hash 0x...
  python HookUp_app.py reference | tips | districts | venue-names
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, List, Optional

APP_NAME = "HookUp"
HOOKUP_VERSION = "1.0.0"
ENGINE_NAME = "AmstaMatchaXXX"

# Defaults (no RPC for Java engine — in-process or remote API)
DEFAULT_ENGINE_URL = os.environ.get("HOOKUP_ENGINE_URL", "")

# Venue types (match Java AMMVenueType)
VENUE_TYPES = ["CANAL_HOUSE", "LOUNGE", "PRIVATE_STUDIO", "EXPERIENCE_ROOM"]
# EIP-55 addresses used in AmstaMatchaXXX (40 hex)
AMM_CURATOR = "0xCd2A3d9F1E7b4C6a8D0e2F5A7c9B1d3E6f8A0C2"
AMM_TREASURY = "0xBe1F4a7C0d3E6b9F2a5C8d1E4f7A0b3D6e9F2a5"
AMM_MESSAGE_RELAY = "0x9F2e5A8c1D4f7B0a3E6d9C2f5A8b1E4d7C0a3F6"
AMM_FEE_COLLECTOR = "0x8E1d4F7a0C3e6B9f2A5c8D1e4F7a0B3d6E9f2A5"
AMM_BACKUP_CURATOR = "0x7D0c3F6a9E2b5D8f1A4c7E0b3F6a9D2e5C8f1B4"
AMM_ZERO = "0x0000000000000000000000000000000000000000"

# Districts (Amsterdam theme)
DISTRICTS = [
    "Centrum", "Jordaan", "De Pijp", "West", "Oost", "Noord", "Zuid", "Grachtengordel"
]

# Venue name suggestions (Amsterdam tour guide theme)
VENUE_NAME_SUGGESTIONS = [
    "Herengracht View", "Keizersgracht Suite", "Prinsengracht Room",
    "Jordaan Hideaway", "De Pijp Lounge", "Nine Streets Studio",
    "Canal House One", "Canal House Two", "Private Lounge A",
    "Central Canal Suite", "West Side Studio", "East Side Lounge",
]

# Error codes (AMM_ prefix from Java)
ERROR_CODES = [
    "AMM_ZERO_ADDRESS", "AMM_ZERO_AMOUNT", "AMM_VENUE_NOT_FOUND", "AMM_SLOT_NOT_FOUND",
    "AMM_BOOKING_NOT_FOUND", "AMM_MESSAGE_NOT_FOUND", "AMM_NOT_CURATOR", "AMM_NOT_GUIDE",
    "AMM_SLOT_UNAVAILABLE", "AMM_BOOKING_EXISTS", "AMM_MAX_VENUES", "AMM_MAX_SLOTS",
    "AMM_MAX_BOOKINGS", "AMM_MAX_MESSAGES", "AMM_NAMESPACE_FROZEN", "AMM_REENTRANT",
    "AMM_INVALID_FEE", "AMM_INVALID_DURATION", "AMM_MESSAGE_DISABLED",
]


def cmd_config(args: argparse.Namespace) -> int:
    print("APP_NAME:", APP_NAME)
    print("HOOKUP_VERSION:", HOOKUP_VERSION)
    print("ENGINE_NAME:", ENGINE_NAME)
    print("HOOKUP_ENGINE_URL:", DEFAULT_ENGINE_URL or "(not set)")
    print("AMM_CURATOR:", AMM_CURATOR)
    print("AMM_TREASURY:", AMM_TREASURY)
    return 0


