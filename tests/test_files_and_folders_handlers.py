import re
import shutil
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from uuid import uuid4
from zipfile import ZipFile

import pytest
from sqlalchemy import select

from confiacim_api.errors import (
    LoadsFileEmptyError,
    LoadsFileNotFoundInZipError,
    MaterialsFileEmptyError,
    MaterialsFileNotFoundInZipError,
    MaterialsFileValueError,
)
from confiacim_api.files_and_folders_handlers import (
    add_nocliprc_macro,
    clean_temporary_simulation_folder,
    extract_loads_infos,
    extract_loads_infos_from_blob,
    extract_materials_infos,
    extract_materials_infos_from_blob,
    new_time_loop,
    read_loads_file,
    read_materials_file,
    remove_tab_and_unnecessary_spaces,
    rewrite_case_file,
    rm_nocliprc_macro,
    rm_setpnode_and_setptime,
    save_generated_form_files,
    save_zip_in_db,
    temporary_simulation_folder,
    unzip_file,
    unzip_tencim_case,
    zip_generated_form_case,
)
from confiacim_api.models import Case
from tests.constants import (
    CASE_FILE,
    LOADS_FILE,
    MATERIALS_FILE,
    NEW_CASE_FILE_LAST_STEP_3,
    RES_CASE_FILE_1,
    RES_CASE_FILE_2,
    RES_CASE_FILE_3,
    RES_CASE_FILE_4,
)


@pytest.mark.integration
def test_positive_create_temporary_simulation_folder(tmp_path):

    dir_path = temporary_simulation_folder(tmp_path)
    list_dir = [d.name for d in tmp_path.iterdir() if d.is_dir()]

    assert len(list_dir) == 1
    assert dir_path.name.endswith(list_dir[0])


@pytest.mark.integration
def test_positive_unzip_file(tmp_path):

    tmp_dir = TemporaryDirectory(dir=tmp_path)
    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        unzip_file(fp, tmp_dir)

    list_dir = {d.name for d in Path(tmp_dir.name).iterdir()}

    expected = {
        "loads.dat",
        "initialtemperature.dat",
        "case.dat",
        "adiabat.dat",
        "mesh.dat",
        "initialstress.dat",
        "materials.dat",
    }

    assert list_dir == expected


@pytest.mark.integration
def test_positive_create_unzip_and_clean_simulation_folder(tmp_path):

    tmp_dir = temporary_simulation_folder(tmp_path)

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        unzip_file(fp, tmp_dir)

    list_dir = list(Path(tmp_dir.name).iterdir())

    assert len(list_dir) == 7

    clean_temporary_simulation_folder(tmp_dir)

    list_dir = list(tmp_path.iterdir())

    assert len(list_dir) == 0


@pytest.mark.integration
def test_unzip_tencim_case_from_db(session, user, tmp_path):

    tmp_dir = temporary_simulation_folder(tmp_path)

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        case = Case(tag="case1", user=user, base_file=fp.read())
        session.add(case)
        session.commit()
        session.reset()

    case_from_db = session.scalar(select(Case).where(Case.tag == "case1"))

    unzip_tencim_case(case_from_db, tmp_dir)

    list_dir = {d.name for d in Path(tmp_dir.name).iterdir()}

    assert len(list_dir) == 7

    expected = {
        "loads.dat",
        "initialtemperature.dat",
        "case.dat",
        "adiabat.dat",
        "mesh.dat",
        "initialstress.dat",
        "materials.dat",
    }

    assert list_dir == expected


@pytest.mark.unit
def test_add_nocliprc_macro():

    with open("tests/fixtures/case.dat") as fp:
        case_file = fp.read()

    assert "nocliprc\n" not in case_file

    new_file = add_nocliprc_macro(case_file)

    assert "end mesh\nnocliprc\n" in new_file


@pytest.mark.unit
def test_remove_nocliprc_macro():

    with open("tests/fixtures/case_nocliprc.dat") as fp:
        case_file = fp.read()

    assert "nocliprc\n" in case_file

    new_file = rm_nocliprc_macro(case_file)

    assert "nocliprc\n" not in new_file


@pytest.mark.unit
def test_case_file_must_have_only_one_nocliprc_macro():

    with open("tests/fixtures/case_nocliprc.dat") as fp:
        case_file = fp.read()

    assert case_file.count("nocliprc") == 1

    new_file = add_nocliprc_macro(case_file)

    assert new_file.count("nocliprc") == 1


@pytest.mark.unit
def test_rewrite_case_file_with_nocliprc(tmp_path):

    shutil.copy2("tests/fixtures/case.dat", tmp_path)

    case_path = tmp_path / "case.dat"

    assert "nocliprc" not in case_path.read_text()

    rewrite_case_file(task_id=uuid4(), case_path=case_path, rc_limit=False)

    assert case_path.read_text().count("nocliprc") == 1


@pytest.mark.unit
def test_rewrite_case_file_without_setpnode_and_setptime(tmp_path):

    shutil.copy2("tests/fixtures/case.dat", tmp_path)

    case_path = tmp_path / "case.dat"

    content = case_path.read_text()

    assert "setpnode" in content
    assert "setptime" in content

    rewrite_case_file(task_id=uuid4(), case_path=case_path, setpnode_and_setptime=True)

    content = case_path.read_text()
    assert "setpnode" not in content
    assert "setptime" not in content


@pytest.mark.unit
def test_rewrite_case_file_with_nocliprc_without_setpnode_and_setptime(tmp_path):

    shutil.copy2("tests/fixtures/case.dat", tmp_path)

    case_path = tmp_path / "case.dat"

    content = case_path.read_text()

    assert "nocliprc" not in content
    assert "setpnode" in content
    assert "setptime" in content

    rewrite_case_file(task_id=uuid4(), case_path=case_path)

    content = case_path.read_text()

    assert "nocliprc" in content
    assert "setpnode" not in content
    assert "setptime" not in content


@pytest.mark.unit
def test_rm_setpnode_and_setptime():

    with open("tests/fixtures/case.dat") as fp:
        case_file = fp.read()

    new_file = rm_setpnode_and_setptime(case_file)

    assert "setpnode" not in new_file
    assert "setptime" not in new_file


@pytest.mark.unit
def test_rewrite_case_file_with_new_loop_time(tmp_path):

    shutil.copy2("tests/fixtures/case.dat", tmp_path)

    case_path = tmp_path / "case.dat"

    content = case_path.read_text()

    assert "nocliprc" not in content
    assert "setpnode" in content
    assert "setptime" in content

    rewrite_case_file(task_id=uuid4(), case_path=case_path, critical_point=3)

    content = case_path.read_text()

    assert content == NEW_CASE_FILE_LAST_STEP_3


@pytest.mark.unit
@pytest.mark.parametrize(
    "last_step, result_file",
    [
        (1, RES_CASE_FILE_1),
        (9, RES_CASE_FILE_2),
        (11, RES_CASE_FILE_3),
        (20, RES_CASE_FILE_4),
        (100, CASE_FILE),
    ],
    ids=["step 1", "step 9", "step 11", "step 20", "step 100"],
)
def test_new_time_loop(last_step: int, result_file):

    new_case = new_time_loop(case_file_str=CASE_FILE, last_step=last_step)

    assert new_case == result_file


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


@pytest.mark.unit
def test_zip_form_case(tmp_path):
    with open("tests/fixtures/case_form_generated.zip", mode="rb") as file:
        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(tmp_path)

    zip_generated_form_case(tmp_path)

    expected_zip_generated = tmp_path / "tmp_case_form.zip"

    assert expected_zip_generated.exists() is True

    with ZipFile(expected_zip_generated, "r") as zip_ref:
        assert set(zip_ref.namelist()) == {
            "materials.dat",
            "templates/materials.jinja",
            "mesh.dat",
            "case.yml",
            "case.dat",
            "loads.dat",
            "initialtemperature.dat",
        }


@pytest.mark.integration
def test_salve_the_zip_in_db(session, tmp_path, form_results):

    shutil.copy2("tests/fixtures/case_form_generated.zip", tmp_path)

    save_zip_in_db(session, tmp_path / "case_form_generated.zip", form_results)

    assert form_results.generated_case_files is not None

    with ZipFile(BytesIO(form_results.generated_case_files), "r") as zip_ref:
        assert set(zip_ref.namelist()) == {
            "materials.dat",
            "templates/materials.jinja",
            "mesh.dat",
            "case.yml",
            "case.dat",
            "loads.dat",
            "initialtemperature.dat",
            "templates/",
        }


@pytest.mark.integration
def test_save_generated_form_files(session, tmp_path, form_results):
    with open("tests/fixtures/case_form_generated.zip", mode="rb") as file:
        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(tmp_path)

    save_generated_form_files(session, tmp_path, form_results)

    assert form_results.generated_case_files is not None

    assert (tmp_path / "tmp_case_form.zip").exists() is False

    with ZipFile(BytesIO(form_results.generated_case_files), "r") as zip_ref:
        assert set(zip_ref.namelist()) == {
            "materials.dat",
            "templates/materials.jinja",
            "mesh.dat",
            "case.yml",
            "case.dat",
            "loads.dat",
            "initialtemperature.dat",
        }


@pytest.mark.unit
def test_remove_tab_and_unnecessary_spaces():
    case_str = "case  \ndt\t 1 \nend\t \n"
    assert remove_tab_and_unnecessary_spaces(case_str) == "case\ndt 1\nend\n"


@pytest.mark.integration
def test_positive_read_loads():

    path = Path("tests/fixtures/loads.dat")

    loads = read_loads_file(path)

    assert loads.nodalsource == 291.639
    assert loads.mechanical_loads.istep == (0, 600, 1200, 1800)
    assert loads.mechanical_loads.force == (0, 0, 6.8947e07, 6.8947e07)

    assert loads.thermal_loads.istep == (600, 1200, 1800)
    assert loads.thermal_loads.h == (0, 0, 0)
    assert loads.thermal_loads.temperature == (299.073, 299.073, 299.073)


@pytest.mark.unit
def test_positive_extract_loads_infos():

    loads = extract_loads_infos(LOADS_FILE)

    assert loads.nodalsource == 291.639
    assert loads.mechanical_loads.istep == (0, 600, 1200, 1800)
    assert loads.mechanical_loads.force == (0, 0, 6.8947e07, 6.8947e07)

    assert loads.thermal_loads.istep == (600, 1200, 1800)
    assert loads.thermal_loads.h == (15, 15, 15)
    assert loads.thermal_loads.temperature == (299.073, 299.073, 299.073)


@pytest.mark.unit
def test_negative_extract_extract_loads_infos_empty_file():

    with pytest.raises(LoadsFileEmptyError, match="Empty loads file."):
        extract_loads_infos("")


@pytest.mark.unit
def test_positive_extract_loads_infos_from_blob(case_with_real_file):

    loads = extract_loads_infos_from_blob(case_with_real_file)

    assert loads.nodalsource == 329.07
    assert loads.mechanical_loads.istep == (0, 864_000)
    assert loads.mechanical_loads.force == (0, 0)

    assert loads.thermal_loads.istep == (864_000,)
    assert loads.thermal_loads.h == (0.0,)
    assert loads.thermal_loads.temperature == (329.362,)


@pytest.mark.unit
def test_negative_extract_loads_infos_from_blob_zipfile_without_loads(case_with_real_file_without_loads):
    with pytest.raises(LoadsFileNotFoundInZipError, match="Loads file not found in zip."):
        extract_loads_infos_from_blob(case_with_real_file_without_loads)
