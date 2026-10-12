from meow.models.local.event.final_proceedings.event_factory import (
    event_affiliation_factory,
)


def test_street_and_postcode_are_different_fields():
    # keys of the Indico AffiliationSchema (indico/modules/users/schemas.py)
    affiliation = event_affiliation_factory(
        {
            "id": 1,
            "name": " CERN ",
            "street": "Esplanade des Particules 1",
            "postcode": "1211",
            "city": "Meyrin",
            "country_code": "CH",
        }
    )

    assert affiliation.street == "Esplanade des Particules 1"
    assert affiliation.postcode == "1211"
    assert affiliation.name == "CERN"
    data = affiliation.as_dict()
    assert data["street"] != data["postcode"]


def test_missing_street_is_not_replaced_by_the_postcode():
    affiliation = event_affiliation_factory(
        {"name": "Lab", "postcode": "1211", "city": "Meyrin", "country_code": "CH"}
    )

    assert affiliation.street is None
    assert affiliation.postcode == "1211"
