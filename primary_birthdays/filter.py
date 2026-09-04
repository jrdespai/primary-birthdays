"""Filter Primary children and teachers from LCR data."""

from __future__ import annotations

import re
from typing import Any

# Typical Primary class progression for display ordering.
CLASS_ORDER = [
    "nursery",
    "sunbeams",
    "ctr 4",
    "ctr 5",
    "ctr 6",
    "ctr 7",
    "valiant 8",
    "valiant 9",
    "valiant 10",
    "valiant 11",
    "valiant 12",
]

PRIMARY_CLASS_PATTERN = re.compile(
    r"^(Nursery|Sunbeams?|CTR \d+|Valiant \d+)$",
    re.IGNORECASE,
)
STAKE_PRIMARY_PATTERN = re.compile(r"stake\s+primary", re.IGNORECASE)


def build_org_lookup(org_nodes: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Map unitOrgUuid -> {org, suborg}."""
    lookup: dict[str, dict[str, str]] = {}

    def walk(node: dict[str, Any], parent_org: str = "") -> None:
        org_name = node.get("unitOrgName") or node.get("name") or ""
        org_uuid = node.get("unitOrgUuid") or node.get("uuid") or node.get("id")
        if org_uuid:
            if parent_org:
                lookup[str(org_uuid)] = {"org": parent_org, "suborg": org_name}
            else:
                lookup[str(org_uuid)] = {"org": org_name, "suborg": ""}

        for child in node.get("children") or []:
            walk(child, parent_org=org_name if not parent_org else parent_org)

    for node in org_nodes:
        walk(node)

    return lookup


def _normalize_class_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip())


def class_sort_key(class_name: str) -> tuple[int, str]:
    normalized = class_name.lower().strip()
    for index, label in enumerate(CLASS_ORDER):
        if label in normalized or normalized == label:
            return (index, class_name.lower())
    return (len(CLASS_ORDER), class_name.lower())


def _member_name(member: dict[str, Any]) -> str:
    formats = member.get("nameFormats") or {}
    if formats.get("listPreferredLocal"):
        return formats["listPreferredLocal"]
    if formats.get("spokenPreferredLocal"):
        return formats["spokenPreferredLocal"]
    return member.get("displayName") or member.get("name") or "Unknown"


MONTH_ABBR = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def _birthday_fields(member: dict[str, Any]) -> tuple[str, str]:
    display = member.get("birthDateDisplay") or member.get("birthDateFormatted") or ""
    sort_raw = str(member.get("birthDateSort") or member.get("birthDaySort") or "")

    mmdd = ""
    if re.match(r"\d{4}-\d{2}-\d{2}", sort_raw):
        mmdd = sort_raw[5:7] + sort_raw[8:10]
    elif len(sort_raw) >= 8 and sort_raw[:4].isdigit() and sort_raw[4:8].isdigit():
        mmdd = sort_raw[4:8]
    else:
        text_match = re.match(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", display)
        if text_match:
            day, month_name, _year = text_match.groups()
            month_num = MONTH_ABBR.get(month_name[:3].title())
            if month_num:
                mmdd = f"{month_num:02d}{int(day):02d}"
        else:
            parts = re.findall(r"\d+", display)
            if len(parts) >= 3:
                if len(parts[0]) == 4:
                    mmdd = f"{parts[1].zfill(2)}{parts[2].zfill(2)}"
                else:
                    mmdd = f"{parts[0].zfill(2)}{parts[1].zfill(2)}"

    return display, mmdd


def index_members_by_uuid(members: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(m["uuid"]): m for m in members if m.get("uuid")}


def _is_ward_primary_calling(organization: str, org_name: str = "Primary") -> bool:
    if not organization.strip():
        return False
    if STAKE_PRIMARY_PATTERN.search(organization):
        return False
    org_lower = organization.lower()
    if org_name.lower() in org_lower:
        return True
    if "primary activities" in org_lower:
        return True
    return False


def _is_included_primary_calling(
    organization: str,
    position: str,
    calling_name: str,
    org_name: str = "Primary",
) -> bool:
    if not _is_ward_primary_calling(organization, org_name):
        return False

    text = f"{organization} {position} {calling_name}".lower()

    if "teacher" in text:
        return True
    if any(kw in text for kw in ("president", "counselor", "secretary")):
        return True
    if any(kw in text for kw in ("music", "chorister", "pianist", "organist")):
        return True
    if "activities" in text and "leader" in text:
        return True
    if "nursery" in text and "leader" in text:
        return True

    return False


def _calling_role_category(organization: str, position: str, calling_name: str) -> str:
    text = f"{organization} {position} {calling_name}".lower()
    if "teacher" in text:
        return "Teacher"
    if any(kw in text for kw in ("music", "chorister", "pianist", "organist")):
        return "Music"
    if "activities" in text and "leader" in text:
        return "Activities"
    if "nursery" in text and "leader" in text:
        return "Nursery"
    if any(kw in text for kw in ("president", "counselor", "secretary")):
        return "Presidency"
    return "Leader"


def _leader_group_label(
    organization: str,
    position: str,
    calling_name: str,
    class_name: str,
    gender: str = "",
) -> str:
    org_lower = organization.lower()
    text = f"{organization} {position} {calling_name}".lower()

    if "primary activities" in org_lower:
        return organization
    if "valiant activities leader" in text:
        gender_upper = gender.upper()
        if gender_upper == "MALE":
            return "Primary Activities - Boys"
        if gender_upper == "FEMALE":
            return "Primary Activities - Girls"
    if any(kw in text for kw in ("music", "chorister", "pianist", "organist")):
        return "Music"
    if "nursery" in text and "leader" in text:
        return "Nursery"
    if any(kw in text for kw in ("president", "counselor", "secretary")):
        return "Primary Presidency"
    if class_name:
        return class_name
    return organization or "Primary"


def extract_primary_leader_uuids(
    callings_data: dict[str, Any],
    org_name: str = "Primary",
) -> set[str]:
    uuids: set[str] = set()

    members_with = callings_data.get("membersWithCallings") or {}
    for person in members_with.values():
        uuid = person.get("uuid")
        if not uuid:
            continue
        for calling_name, calling_info in (person.get("callings") or {}).items():
            organization = (
                calling_info.get("organization")
                or calling_info.get("organizationName")
                or calling_info.get("unitName")
                or ""
            )
            position = calling_info.get("position") or calling_name or ""
            if _is_included_primary_calling(
                organization, position, calling_name, org_name
            ):
                uuids.add(str(uuid))

    return uuids


def extract_primary_leaders(
    callings_data: dict[str, Any],
    members_by_uuid: dict[str, dict[str, Any]],
    org_name: str = "Primary",
) -> list[dict[str, Any]]:
    leaders: list[dict[str, Any]] = []
    seen: set[str] = set()

    members_with = callings_data.get("membersWithCallings") or {}
    for person in members_with.values():
        uuid = person.get("uuid")
        if not uuid:
            continue

        for calling_name, calling_info in (person.get("callings") or {}).items():
            organization = (
                calling_info.get("organization")
                or calling_info.get("organizationName")
                or ""
            )
            position = calling_info.get("position") or calling_name or ""

            if not _is_included_primary_calling(
                organization, position, calling_name, org_name
            ):
                continue

            dedupe_key = f"{uuid}:{position}:{calling_name}"
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            member = members_by_uuid.get(str(uuid), {})
            name = _member_name(member) if member else person.get("name") or "Unknown"
            birthday, mmdd = _birthday_fields(member) if member else ("", "")
            class_name = calling_info.get("className") or _infer_teacher_class(
                organization, position
            )
            group_label = _leader_group_label(
                organization,
                position,
                calling_name,
                class_name,
                gender=str(member.get("gender") or member.get("sex") or ""),
            )

            leaders.append(
                {
                    "uuid": str(uuid),
                    "name": name,
                    "birthday": birthday,
                    "mmdd": mmdd,
                    "age": member.get("age") if member else "",
                    "role": _calling_role_category(organization, position, calling_name),
                    "class": group_label,
                    "position": position,
                }
            )

    return leaders


# Backward-compatible aliases
extract_primary_teacher_uuids = extract_primary_leader_uuids
extract_primary_teachers = extract_primary_leaders


def _infer_teacher_class(organization: str, position: str) -> str:
    """Pull class name from calling text when possible."""
    for source in (position, organization):
        lower = source.lower()
        for label in CLASS_ORDER:
            if label in lower:
                return label.title() if label != "ctr 4" else "CTR 4"
        match = re.search(
            r"(Sunbeams?|Nursery|CTR\s*\d+|Valiant\s*\d+)",
            source,
            re.IGNORECASE,
        )
        if match:
            return _normalize_class_name(match.group(1))
    return ""


def extract_primary_children(
    members: list[dict[str, Any]],
    org_map: dict[str, str],
    leader_uuids: set[str],
) -> list[dict[str, Any]]:
    """Identify Primary children using member associatedOrgUuids and org labels."""
    children: list[dict[str, Any]] = []
    seen: set[str] = set()

    for member in members:
        uuid = member.get("uuid")
        if not uuid:
            continue
        uuid = str(uuid)
        if uuid in leader_uuids or uuid in seen:
            continue

        primary_classes: list[str] = []
        for org_id in member.get("associatedOrgUuids") or []:
            label = _normalize_class_name(org_map.get(str(org_id), ""))
            if label and PRIMARY_CLASS_PATTERN.match(label):
                primary_classes.append(label)

        if not primary_classes:
            continue

        seen.add(uuid)
        birthday, mmdd = _birthday_fields(member)
        children.append(
            {
                "uuid": uuid,
                "name": _member_name(member),
                "birthday": birthday,
                "mmdd": mmdd,
                "age": member.get("age", ""),
                "role": "Child",
                "class": primary_classes[0],
                "position": "",
            }
        )

    return children
