"""Tests for org map parsing."""

from primary_birthdays.fetch import parse_org_map_from_rsc


def test_parse_org_map_from_rsc():
    body = (
        '{"children":[{"label":"Valiant 9","value":"abc","orgUuid":"uuid-9","children":null},'
        '{"label":"Sunbeams","value":"def","orgUuid":"uuid-sun","children":null}]}'
    )
    org_map = parse_org_map_from_rsc(body)
    assert org_map["uuid-9"] == "Valiant 9"
    assert org_map["uuid-sun"] == "Sunbeams"
