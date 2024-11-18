import re
from pathlib import Path
from textwrap import dedent

import pytest

from confiacim_api.errors import (
    MaterialsFileEmptyError,
    MaterialsFileNotFoundInZipError,
    MaterialsFileValueError,
)
from confiacim_api.files_and_folders_handlers import (
    extract_materials_infos,
    extract_materials_infos_from_blob,
    read_materials_file,
)
from tests.constants import MATERIALS_FILE


@pytest.mark.unit
def test_positive_extract_materials_infos():

    materials = extract_materials_infos(MATERIALS_FILE)

    assert materials.E_c == pytest.approx(1.019e10)
    assert materials.poisson_c == pytest.approx(0.32)
    assert materials.E_f == pytest.approx(2.040e10)
    assert materials.poisson_f == pytest.approx(0.36)


@pytest.mark.unit
def test_negative_extract_materials_infos_empty_file():

    with pytest.raises(MaterialsFileEmptyError, match="Empty materials file"):
        extract_materials_infos("")


@pytest.mark.unit
def test_negative_extract_materials_invalid_mat_number():

    file_str = dedent(
        """\
    materials
        invalid 1 1.999e+11 0.3000 1.400e-05 0 0 4.292e+01 3.894e+06 0 0 0
    end materials
    return"""
    )

    with pytest.raises(
        MaterialsFileValueError,
        match=re.escape("Invalid material number: invalid literal for int() with base 10: 'invalid'"),
    ):
        extract_materials_infos(file_str)


@pytest.mark.unit
def test_negative_extract_materials_invalid_prop_value():

    file_str = dedent(
        """\
    materials
        3 1 invalid 0.3000 1.400e-05 0 0 4.292e+01 3.894e+06 0 0 0
    end materials
    return"""
    )

    with pytest.raises(
        MaterialsFileValueError,
        match="Invalid prop value in material 3: could not convert string to float: 'invalid'",
    ):
        extract_materials_infos(file_str)


@pytest.mark.integration
def test_positive_read_materials():

    path = Path("tests/fixtures/materials.dat")

    materials = read_materials_file(path)

    assert materials.E_c == pytest.approx(1.019e10)
    assert materials.poisson_c == pytest.approx(0.32)
    assert materials.thermal_expansion_c == pytest.approx(9.810e-06)
    assert materials.thermal_conductivity_c == pytest.approx(3.360e00)
    assert materials.volumetric_heat_capacity_c == pytest.approx(2.077e06)
    assert materials.friction_angle_c == pytest.approx(1.500e01)
    assert materials.cohesion_c == pytest.approx(2.540e07)

    assert materials.E_f == pytest.approx(2.040e10)
    assert materials.poisson_f == pytest.approx(0.36)
    assert materials.thermal_expansion_f == pytest.approx(1.000e-05)
    assert materials.thermal_conductivity_f == pytest.approx(6.006e00)
    assert materials.volumetric_heat_capacity_f == pytest.approx(1.901e06)


@pytest.mark.unit
def test_positive_extract_materials_infos_from_blob(case_with_real_file):

    mat_infos = extract_materials_infos_from_blob(case_with_real_file)

    assert mat_infos.E_c == pytest.approx(10960000000.0)
    assert mat_infos.poisson_c == pytest.approx(0.228)
    assert mat_infos.thermal_expansion_c == pytest.approx(1e-5)
    assert mat_infos.thermal_conductivity_c == pytest.approx(1.75)
    assert mat_infos.volumetric_heat_capacity_c == pytest.approx(1869000.0)
    assert mat_infos.friction_angle_c == pytest.approx(14.0)
    assert mat_infos.cohesion_c == pytest.approx(18170000.0)

    assert mat_infos.E_f == pytest.approx(37920000000.0)
    assert mat_infos.poisson_f == pytest.approx(0.21)
    assert mat_infos.thermal_expansion_f == pytest.approx(4.14e-05)
    assert mat_infos.thermal_conductivity_f == pytest.approx(6.006)
    assert mat_infos.volumetric_heat_capacity_f == pytest.approx(1929000.0)


@pytest.mark.unit
def test_negative_extract_materials_infos_from_blob_zipfile_without_materials(case_with_real_file_without_materials):

    with pytest.raises(MaterialsFileNotFoundInZipError, match="Materials file not found in zip."):
        extract_materials_infos_from_blob(case_with_real_file_without_materials)
