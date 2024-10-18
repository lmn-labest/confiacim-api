from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from confiacim_api.models import Case, MaterialsBaseCaseAverageProps


@pytest.mark.integration
def test_create_materials(session: Session, case: Case):

    mat = MaterialsBaseCaseAverageProps(
        case=case,
        E_c=1.0,
        poisson_c=0.1,
        thermal_expansion_c=1.0,
        thermal_conductivity_c=1.0,
        volumetric_heat_capacity_c=2.0,
        friction_angle_c=3.0,
        cohesion_c=2.0,
        E_f=1.5,
        poisson_f=0.2,
        thermal_expansion_f=1.0,
        thermal_conductivity_f=2.0,
        volumetric_heat_capacity_f=3.0,
    )
    session.add(mat)
    session.commit()
    mat_id = mat.id
    case_id = case.id
    session.reset()

    from_db = session.get(MaterialsBaseCaseAverageProps, mat_id)

    assert from_db is not None

    assert from_db is not mat  # Para evitar falso positivos

    assert from_db.id == mat_id
    assert from_db.case.id == case_id
    assert isinstance(from_db.E_c, float)
    assert isinstance(from_db.poisson_c, float)
    assert isinstance(from_db.thermal_expansion_c, float)
    assert isinstance(from_db.thermal_conductivity_c, float)
    assert isinstance(from_db.volumetric_heat_capacity_c, float)
    assert isinstance(from_db.friction_angle_c, float)
    assert isinstance(from_db.cohesion_c, float)

    assert isinstance(from_db.E_f, float)
    assert isinstance(from_db.poisson_f, float)
    assert isinstance(from_db.thermal_expansion_f, float)
    assert isinstance(from_db.thermal_conductivity_f, float)
    assert isinstance(from_db.volumetric_heat_capacity_f, float)

    assert from_db.created_at is not None
    assert isinstance(from_db.created_at, datetime)

    assert from_db.updated_at is not None
    assert isinstance(from_db.updated_at, datetime)


@pytest.mark.unit
def test_str(materials):
    expected = f"MaterialsBaseCaseAverageProps(id={materials.id}, case={materials.case.tag}, E_c={materials.E_c}, ...)"
    assert str(materials) == expected
