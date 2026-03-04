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


def cmd_version(args: argparse.Namespace) -> int:
    print(APP_NAME, HOOKUP_VERSION, "| Engine:", ENGINE_NAME)
    return 0


def cmd_constants(args: argparse.Namespace) -> int:
    print("AmstaMatchaXXX constants:")
    print("  AMM_MAX_VENUES = 384")
    print("  AMM_MAX_SLOTS_PER_VENUE = 96")
    print("  AMM_MAX_BOOKINGS_PER_USER = 24")
    print("  AMM_MAX_MESSAGES_PER_THREAD = 512")
    print("  AMM_MAX_THREADS = 2048")
    print("  AMM_FEE_BPS_CAP = 500")
    print("  AMM_NAMESPACE = amsta-matcha-xxx.v1")
    return 0


def cmd_reference(args: argparse.Namespace) -> int:
    print("""
AmstaMatchaXXX (Java engine) — Amsterdam tour guide, adult industry, optional messaging.

Roles:
  curator / backupCurator — add venues, list slots, set fee, messaging, freeze
  guide — slot lister; can complete bookings
  guest — book tours, cancel own bookings

Venues: addVenue(venueId, name, venueType). Types: CANAL_HOUSE, LOUNGE, PRIVATE_STUDIO, EXPERIENCE_ROOM.
Slots: listSlot(slotId, venueId, startEpoch, endEpoch). Status: OPEN, BOOKED, CANCELLED.
Bookings: bookTour(guest, slotId, amountWei). Status: PENDING, CONFIRMED, COMPLETED, CANCELLED.
Messages (optional): sendMessage(fromAddr, toAddr, contentHash). Threads created on first message.

Addresses (EIP-55, 40 hex): curator, treasury, messageRelay, feeCollector, backupCurator — set in constructor.
""")
    return 0


def cmd_tips(args: argparse.Namespace) -> int:
    for i, tip in enumerate([
        "Use valid EIP-55 addresses (40 hex after 0x) for curator and guests.",
        "Venue names can be any string; use suggest venue-names for ideas.",
        "Slots require startEpoch < endEpoch; duration typically 60–480 minutes.",
        "Booking fee is feeBps (default 45) per 10000 of amountWei.",
        "Messaging can be disabled by curator; threads are created automatically.",
        "Namespace freeze stops new venues and slots; bookings/messages unaffected.",
    ], 1):
        print(f"  {i}. {tip}")
    return 0


def cmd_districts(args: argparse.Namespace) -> int:
    for d in DISTRICTS:
        print(d)
    return 0


def cmd_venue_names(args: argparse.Namespace) -> int:
    for n in VENUE_NAME_SUGGESTIONS:
        print(n)
    return 0


def cmd_errors(args: argparse.Namespace) -> int:
    for c in ERROR_CODES:
        print(c)
    return 0


# -----------------------------------------------------------------------------
# AMSTERDAM TOUR GUIDE REFERENCE (adult industry theme)
# -----------------------------------------------------------------------------

AMSTERDAM_GUIDE_INTRO = """
HookUp links to AmstaMatchaXXX — canal-side discovery and optional messaging for adults.
Venue types: Canal House, Lounge, Private Studio, Experience Room.
Districts: Centrum, Jordaan, De Pijp, West, Oost, Noord, Zuid, Grachtengordel.
"""

DISTRICT_DESCRIPTIONS = {
    "Centrum": "Central canal ring and historic core.",
    "Jordaan": "Narrow streets and local character.",
    "De Pijp": "Vibrant and diverse neighbourhood.",
    "West": "Residential and quieter options.",
    "Oost": "Creative and mixed-use areas.",
    "Noord": "Across IJ, developing district.",
    "Zuid": "Business and upscale residential.",
    "Grachtengordel": "UNESCO canal ring.",
}

VENUE_TYPE_DESCRIPTIONS = {
    "CANAL_HOUSE": "Canal house venue.",
    "LOUNGE": "Lounge setting.",
    "PRIVATE_STUDIO": "Private studio.",
    "EXPERIENCE_ROOM": "Experience room.",
}

def cmd_guide(args: argparse.Namespace) -> int:
    print(AMSTERDAM_GUIDE_INTRO)
    for district, desc in DISTRICT_DESCRIPTIONS.items():
        print(f"  {district}: {desc}")
    return 0


def cmd_venue_types(args: argparse.Namespace) -> int:
    for t, desc in VENUE_TYPE_DESCRIPTIONS.items():
        print(t, "—", desc)
    return 0


# -----------------------------------------------------------------------------
# FULL JAVA ENGINE API REFERENCE
# -----------------------------------------------------------------------------

JAVA_API_REFERENCE = """
AmstaMatchaXXX Java API (single file):

Constructor: AmstaMatchaXXX() — sets curator, treasury, messageRelay, feeCollector, backupCurator (EIP-55), deployEpoch.

Venues:
  addVenue(sender, venueId, name, venueType) -> venueId
  getVenue(venueId) -> AMMVenue
  listVenues() -> List<AMMVenue>
  listVenuesByType(venueType)
  getVenueCount(), venueExists(venueId), getVenueOrThrow(venueId)
  findVenueByName(name) -> Optional<AMMVenue>
  getVenuesByCurator(curatorAddr), countVenuesByCurator(curatorAddr)
  getVenuesPaginated(offset, limit)
  listVenuesSortedByName()
  getVenuesCreatedAfter(epoch)
  getVenueCountByType(type), getVenueTypeCounts()

Slots:
  listSlot(sender, slotId, venueId, startEpoch, endEpoch) -> slotId
  batchListSlots(sender, venueId, List<SlotSpec>) -> added count
  getSlot(slotId), getSlotOrThrow(slotId), slotExists(slotId)
  getSlotIdsByVenue(venueId)
  getAvailableSlotsForVenue(venueId), getOpenSlotsInRange(fromEpoch, toEpoch)
  getSlotsByVenueAndStatus(venueId, status)
  getSlotsForGuide(guideAddr)
  getSlotCount(), getOpenSlotCount(), getSlotCountForVenue(venueId), getOpenSlotCountForVenue(venueId)
  listSlotsSortedByStart(), getSlotsPaginated(offset, limit)
  listAllSlotIds()
  isSlotAvailable(slotId), getSlotDurationSeconds(slotId)
  isSlotInPast(slotId), isSlotOngoing(slotId)
  getSlotStatusCounts()

Bookings:
  bookTour(guest, slotId, amountWei) -> bookingId
  getBooking(bookingId), getBookingOrThrow(bookingId), bookingExists(bookingId)
  getBookingIdsByGuest(guest), cancelBooking(sender, bookingId)
  completeBooking(sender, bookingId)
  getBookingsByGuide(guide), getBookingsByStatus(status)
  getActiveBookingsForGuest(guest), getCompletedBookingsForGuest(guest), getCancelledBookingsForGuest(guest)
  findBookingBySlot(slotId), hasBookingForSlot(slotId)
  getTotalBookedAmountByGuest(guest)
  getBookingsPaginated(offset, limit), listBookingsSortedByCreated()
  getBookingCount(), getConfirmedBookingCount(), getCompletedBookingCount()
  getBookingStatusCounts()

Messaging:
  sendMessage(fromAddr, toAddr, contentHash) -> messageId
  getMessage(messageId), getMessageOrThrow(messageId), messageExists(messageId)
  getMessageIdsByThread(threadId), getMessagesInThread(threadId)
  getThreadId(addr1, addr2), getThreadIdsForParticipant(addr)
  markMessageDelivered(messageId), markMessageRead(messageId)
  getUnreadMessagesFor(toAddr), getUnreadCountFor(toAddr)
  getMessageCount(), getThreadCount(), getMessageCountInThread(threadId)
  hasThread(addr1, addr2), getParticipantPairsForThread(threadId)

Config (curator only):
  setFeeBps(sender, feeBps), setMessagingEnabled(sender, enabled), setNamespaceFrozen(sender, frozen)
  getConfig(), getCurrentFeeBps(), isMessagingEnabled(), isNamespaceFrozen()

Immutables / addresses:
  getCurator(), getTreasury(), getMessageRelay(), getFeeCollector(), getBackupCurator()
  getCuratorAddress(), getTreasuryAddress(), getMessageRelayAddress(), getFeeCollectorAddress(), getBackupCuratorAddress()
  getCuratorHex(), getTreasuryHex(), getMessageRelayHex(), getFeeCollectorHex(), getBackupCuratorHex()
  getImmutablesList(), getZeroAddress(), isCurator(addr)

Stats / summary:
  getTotalFeesCollected(), getFeesCollected(), getEngineSummary()
  getTotalEventCount(), getVenueTypeCounts(), getSlotStatusCounts(), getBookingStatusCounts()
  remainingVenueSlots(), remainingSlotSlots(venueId), remainingBookingSlots(guest)
  canAddVenue(), canListSlot(venueId), canBook(guest), canSendMessage()

Events: getVenueAddedEvents(), getSlotListedEvents(), getTourBookedEvents(), getMessageSentEvents()
"""

def cmd_java_api(args: argparse.Namespace) -> int:
    print(JAVA_API_REFERENCE)
    return 0


def cmd_venues_list(args: argparse.Namespace) -> int:
    print("(In-process: use Java AmstaMatchaXXX instance; listVenues())")
    print("Venue types:", ", ".join(VENUE_TYPES))
    return 0


def cmd_slots_list(args: argparse.Namespace) -> int:
    print("(In-process: use Java engine getSlotIdsByVenue(venueId))")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=f"{APP_NAME} — CLI for {ENGINE_NAME}")
    sub = p.add_subparsers(dest="command", help="Commands")

    sub.add_parser("config", help="Show config").set_defaults(func=cmd_config)
    sub.add_parser("version", help="App version").set_defaults(func=cmd_version)
    sub.add_parser("constants", help="Engine constants").set_defaults(func=cmd_constants)
    sub.add_parser("reference", help="Engine reference").set_defaults(func=cmd_reference)
    sub.add_parser("tips", help="Usage tips").set_defaults(func=cmd_tips)
    sub.add_parser("districts", help="Amsterdam districts").set_defaults(func=cmd_districts)
    sub.add_parser("venue-names", help="Venue name suggestions").set_defaults(func=cmd_venue_names)
    sub.add_parser("errors", help="Error codes").set_defaults(func=cmd_errors)
    sub.add_parser("guide", help="Amsterdam guide intro and districts").set_defaults(func=cmd_guide)
    sub.add_parser("venue-types", help="Venue type descriptions").set_defaults(func=cmd_venue_types)
    sub.add_parser("java-api", help="Full Java engine API reference").set_defaults(func=cmd_java_api)
    sub.add_parser("workflow", help="Workflow steps").set_defaults(func=cmd_workflow)
    sub.add_parser("usage", help="Usage examples").set_defaults(func=cmd_usage)
    sub.add_parser("addresses", help="Engine addresses").set_defaults(func=cmd_addresses)
    sub.add_parser("quickstart", help="Quick start").set_defaults(func=cmd_quickstart)
    sub.add_parser("extended-venue-names", help="Extended venue name list").set_defaults(func=cmd_extended_venue_names)
    sub.add_parser("amsterdam-tips", help="Amsterdam tips list").set_defaults(func=cmd_amsterdam_tips)
    sub.add_parser("commands", help="List all commands").set_defaults(func=cmd_commands)
    sub.add_parser("long-ref", help="Long reference").set_defaults(func=cmd_long_ref)
    sub.add_parser("padding", help="Padding reference").set_defaults(func=cmd_padding)
    sub.add_parser("paragraphs", help="Paragraph reference").set_defaults(func=cmd_paragraphs)

    v = sub.add_parser("venues", help="Venue commands")
    v_sub = v.add_subparsers(dest="subcommand")
    v_sub.add_parser("list", help="List venues").set_defaults(func=cmd_venues_list)
    v_sub.add_parser("add", help="Add venue (needs Java engine)").set_defaults(func=cmd_venues_list)

    s = sub.add_parser("slots", help="Slot commands")
    s_sub = s.add_subparsers(dest="subcommand")
    s_sub.add_parser("list", help="List slots").set_defaults(func=cmd_slots_list)
    s_sub.add_parser("add", help="Add slot").set_defaults(func=cmd_slots_list)

    sub.add_parser("book", help="Book tour").set_defaults(func=lambda a: (print("Use Java engine bookTour(guest, slotId, amountWei)"), 0)[1])
    sub.add_parser("message", help="Send message").set_defaults(func=lambda a: (print("Use Java engine sendMessage(from, to, contentHash)"), 0)[1])

    args = p.parse_args()
    if not args.command:
        p.print_help()
        return 0
    if args.command == "venues" or args.command == "slots":
        if not getattr(args, "subcommand", None):
            p.print_help()
            return 0
    f = getattr(args, "func", None)
    if f is None:
        p.print_help()
        return 0
    return f(args)


# -----------------------------------------------------------------------------
# WORKFLOW & USAGE (extended)
# -----------------------------------------------------------------------------

WORKFLOW_TEXT = """
HookUp + AmstaMatchaXXX workflow:

1. Start Java engine: new AmstaMatchaXXX(). Addresses are set in constructor.
2. Curator adds venues: addVenue(curatorAddr, venueId, name, CANAL_HOUSE|LOUNGE|PRIVATE_STUDIO|EXPERIENCE_ROOM).
3. Curator lists slots: listSlot(curatorAddr, slotId, venueId, startEpoch, endEpoch).
4. Guest books: bookTour(guestAddr, slotId, amountWei). Fee is deducted per feeBps.
5. Guide or curator completes: completeBooking(sender, bookingId).
6. Optional: sendMessage(fromAddr, toAddr, contentHash) — creates thread if needed.
7. Curator can setFeeBps, setMessagingEnabled, setNamespaceFrozen.
"""

def cmd_workflow(args: argparse.Namespace) -> int:
    print(WORKFLOW_TEXT)
    return 0


USAGE_EXAMPLES = """
Usage examples:

  python HookUp_app.py config
  python HookUp_app.py version
  python HookUp_app.py constants
