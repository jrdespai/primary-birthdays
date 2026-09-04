"""Unit tests for filter and report modules."""

from primary_birthdays.filter import (
    _is_included_primary_calling,
    extract_primary_children,
    extract_primary_leader_uuids,
    extract_primary_leaders,
    index_members_by_uuid,
)
from primary_birthdays.report import build_report


SAMPLE_MEMBERS = [
    {
        "uuid": "child-1",
        "nameFormats": {"listPreferredLocal": "Anderson, Emma"},
        "age": 5,
        "birthDateDisplay": "15 Mar 2020",
        "birthDateSort": "20200315",
        "associatedOrgUuids": ["org-sunbeams", "org-primary"],
    },
    {
        "uuid": "child-2",
        "nameFormats": {"listPreferredLocal": "Brown, Liam"},
        "age": 7,
        "birthDateDisplay": "04 Jul 2018",
        "birthDateSort": "20180704",
        "associatedOrgUuids": ["org-ctr7", "org-primary"],
    },
    {
        "uuid": "teacher-1",
        "nameFormats": {"listPreferredLocal": "Clark, Sarah"},
        "age": 32,
        "birthDateDisplay": "10 Jan 1993",
        "birthDateSort": "19930110",
        "associatedOrgUuids": ["org-sunbeams"],
    },
    {
        "uuid": "pres-1",
        "nameFormats": {"listPreferredLocal": "Jones, Mary"},
        "age": 40,
        "birthDateDisplay": "05 Apr 1985",
        "birthDateSort": "19850405",
    },
    {
        "uuid": "music-1",
        "nameFormats": {"listPreferredLocal": "Smith, Anna"},
        "age": 35,
        "birthDateDisplay": "12 Jun 1990",
        "birthDateSort": "19900612",
    },
    {
        "uuid": "act-1",
        "nameFormats": {"listPreferredLocal": "Davis, Kim"},
        "age": 38,
        "birthDateDisplay": "01 Aug 1987",
        "birthDateSort": "19870801",
    },
]

SAMPLE_ORG_MAP = {
    "org-primary": "Primary",
    "org-sunbeams": "Sunbeams",
    "org-ctr7": "CTR 7",
}

SAMPLE_CALLINGS = {
    "membersWithCallings": {
        "Clark, Sarah": {
            "uuid": "teacher-1",
            "name": "Clark, Sarah",
            "callings": {
                "Primary Teacher": {
                    "organization": "Primary",
                    "position": "Primary Teacher",
                    "className": "Sunbeams",
                }
            },
        },
        "Jones, Mary": {
            "uuid": "pres-1",
            "name": "Jones, Mary",
            "callings": {
                "Primary President": {
                    "organization": "Primary",
                    "position": "Primary President",
                }
            },
        },
        "Smith, Anna": {
            "uuid": "music-1",
            "name": "Smith, Anna",
            "callings": {
                "Primary Music Leader": {
                    "organization": "Primary",
                    "position": "Primary Music Leader",
                }
            },
        },
        "Davis, Kim": {
            "uuid": "act-1",
            "name": "Davis, Kim",
            "callings": {
                "Primary Activities Leader": {
                    "organization": "Primary Activities - Boys",
                    "position": "Primary Activities Leader",
                }
            },
        },
    }
}


def test_included_primary_calling_categories():
    assert _is_included_primary_calling("Primary", "Primary Teacher", "Primary Teacher")
    assert _is_included_primary_calling("Primary", "Primary President", "Primary President")
    assert _is_included_primary_calling("Primary", "Primary Music Leader", "Primary Music Leader")
    assert _is_included_primary_calling(
        "Primary Activities - Girls",
        "Primary Activities Leader",
        "Primary Activities Leader",
    )
    assert _is_included_primary_calling("Primary", "", "Nursery Leader")
    assert not _is_included_primary_calling(
        "Stake Primary",
        "Stake Primary Music Leader",
        "Stake Primary Music Leader",
    )


def test_extract_primary_children_excludes_leaders():
    leader_uuids = extract_primary_leader_uuids(SAMPLE_CALLINGS)
    children = extract_primary_children(SAMPLE_MEMBERS, SAMPLE_ORG_MAP, leader_uuids)
    names = {c["name"] for c in children}
    assert "Anderson, Emma" in names
    assert "Brown, Liam" in names
    assert "Clark, Sarah" not in names
    assert {c["class"] for c in children} == {"Sunbeams", "CTR 7"}


def test_leader_group_label_activities_by_gender():
    from primary_birthdays.filter import _leader_group_label

    assert (
        _leader_group_label(
            "Primary",
            "Valiant Activities Leader",
            "Valiant Activities Leader",
            "",
            gender="MALE",
        )
        == "Primary Activities - Boys"
    )
    assert (
        _leader_group_label(
            "Primary",
            "Valiant Activities Leader",
            "Valiant Activities Leader",
            "",
            gender="FEMALE",
        )
        == "Primary Activities - Girls"
    )


def test_extract_primary_leaders_includes_presidency_music_activities():
    members_by_uuid = index_members_by_uuid(SAMPLE_MEMBERS)
    leaders = extract_primary_leaders(SAMPLE_CALLINGS, members_by_uuid)
    by_role = {leader["role"] for leader in leaders}
    assert by_role == {"Teacher", "Presidency", "Music", "Activities"}
    classes = {leader["class"] for leader in leaders}
    assert "Primary Presidency" in classes
    assert "Music" in classes
    assert "Primary Activities - Boys" in classes


def test_build_report_ordering():
    members_by_uuid = index_members_by_uuid(SAMPLE_MEMBERS)
    leader_uuids = extract_primary_leader_uuids(SAMPLE_CALLINGS)
    children = extract_primary_children(SAMPLE_MEMBERS, SAMPLE_ORG_MAP, leader_uuids)
    leaders = extract_primary_leaders(SAMPLE_CALLINGS, members_by_uuid)
    report = build_report(children, leaders)

    assert report["totals"]["children"] == 2
    assert report["totals"]["leaders"] == 4
    assert report["totals"]["all"] == 6
    assert report["by_month"]["January"][0]["name"] == "Clark, Sarah"
    assert report["by_month"]["March"][0]["name"] == "Anderson, Emma"


def test_build_report_month_filter():
    members_by_uuid = index_members_by_uuid(SAMPLE_MEMBERS)
    leader_uuids = extract_primary_leader_uuids(SAMPLE_CALLINGS)
    children = extract_primary_children(SAMPLE_MEMBERS, SAMPLE_ORG_MAP, leader_uuids)
    leaders = extract_primary_leaders(SAMPLE_CALLINGS, members_by_uuid)
    report = build_report(children, leaders, month=3)
    assert report["totals"]["children"] == 1
    assert report["flat_rows"][0]["name"] == "Anderson, Emma"
