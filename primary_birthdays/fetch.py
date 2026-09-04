"""Fetch member, calling, and organization data from LCR."""

from __future__ import annotations

import logging
import re
from typing import Any

from lcr import API as LcrApi
from lcr import _parse_rsc_object

_LOGGER = logging.getLogger(__name__)

LCR_BASE = "https://lcr.churchofjesuschrist.org"
MEMBER_LIST_URL = f"{LCR_BASE}/mlt/records/member-list?lang=eng"


def fetch_member_list(api: LcrApi) -> list[dict[str, Any]]:
    members, _org_map = fetch_members_and_org_map(api)
    return members


def fetch_members_and_org_map(api: LcrApi) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """
    Fetch ward members and Primary class org UUID mappings from the member-list RSC stream.

    The /mlt/ member list embeds an organization tree (label + orgUuid) alongside members'
    associatedOrgUuids, which replaces the retired class-attendance overview API.
    """
    body = api._capture_rsc(MEMBER_LIST_URL)
    members = _parse_rsc_object(body, '{"members":[', "members")
    if not members:
        raise RuntimeError(
            "Could not parse member-list RSC response. The /mlt/ page "
            "layout or server-action format may have changed."
        )

    org_map = parse_org_map_from_rsc(body)
    _LOGGER.info(
        "Fetched %d members and %d organization labels from member list",
        len(members),
        len(org_map),
    )
    return members, org_map


def parse_org_map_from_rsc(body: str) -> dict[str, str]:
    """Extract orgUuid -> class label mappings from the member-list RSC payload."""
    org_map: dict[str, str] = {}

    for match in re.finditer(
        r'"label":"([^"]+)","value":"[^"]*","orgUuid":"([^"]+)"',
        body,
    ):
        label, org_uuid = match.group(1), match.group(2)
        org_map[org_uuid] = label

    for match in re.finditer(
        r'"orgUuid":"([^"]+)"[^}]{0,120}"label":"([^"]+)"',
        body,
    ):
        org_uuid, label = match.group(1), match.group(2)
        org_map.setdefault(org_uuid, label)

    return org_map


def fetch_members_with_callings(api: LcrApi) -> dict[str, Any]:
    data = api.members_with_callings_list()
    _LOGGER.info("Fetched members-with-callings report")
    return data
