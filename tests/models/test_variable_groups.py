from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from confiacim_api.models import Case, VariableGroup


@pytest.mark.integration
def test_create_variable_group(session: Session, case: Case):

    variable_group = VariableGroup(
        tag="group_a",
        case=case,
        variables={
            "list": [
                {
                    "name": "E_c",
                    "dist": {
                        "name": "lognormal",
                        "params": {
                            "param1": 1.0,
                            "param2": 0.1,
                        },
                    },
                },
                {
                    "name": "poisson_c",
                    "dist": {
                        "name": "lognormal",
                        "params": {
                            "param1": 1.0,
                            "param2": 0.1,
                        },
                    },
                },
                {
                    "name": "internal_pressure",
                    "dist": {
                        "name": "lognormal",
                        "params": {
                            "param1": 1.0,
                            "param2": 0.1,
                        },
                    },
                },
            ]
        },
        correlations={
            "E_c, poisson_c": 0.5,
            "E_c, internal_pressure": 0.2,
        },
    )

    session.add(variable_group)
    session.commit()
    variable_group_id = variable_group.id
    case_id = case.id
    session.reset()

    variable_group_from_db = session.get(VariableGroup, variable_group_id)

    assert variable_group_from_db is not None

    assert variable_group_from_db is not variable_group  # Para evitar falso positivos

    assert variable_group_from_db.id == variable_group_id
    assert variable_group_from_db.case.id == case_id

    assert variable_group_from_db.tag == "group_a"
    assert variable_group_from_db.variables == {
        "list": [
            {
                "name": "E_c",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "param1": 1.0,
                        "param2": 0.1,
                    },
                },
            },
            {
                "name": "poisson_c",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "param1": 1.0,
                        "param2": 0.1,
                    },
                },
            },
            {
                "name": "internal_pressure",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "param1": 1.0,
                        "param2": 0.1,
                    },
                },
            },
        ]
    }

    assert variable_group_from_db.correlations == {
        "E_c, poisson_c": 0.5,
        "E_c, internal_pressure": 0.2,
    }

    assert variable_group_from_db.created_at is not None
    assert isinstance(variable_group_from_db.created_at, datetime)

    assert variable_group_from_db.updated_at is not None
    assert isinstance(variable_group_from_db.updated_at, datetime)


@pytest.mark.unit
def test_str(variable_group):
    assert str(variable_group) == f"VariableGroup(id={variable_group.id}, tag={variable_group.tag})"
