import shutil
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4
from zipfile import ZipFile

import pytest
from sqlalchemy import select

from confiacim_api.files_and_folders_handlers import (
    add_nocliprc_macro,
    clean_temporary_simulation_folder,
    new_time_loop,
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
        "hidrationprop.dat",
    }

    assert list_dir == expected


@pytest.mark.integration
def test_positive_create_unzip_and_clean_simulation_folder(tmp_path):

    tmp_dir = temporary_simulation_folder(tmp_path)

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        unzip_file(fp, tmp_dir)

    list_dir = list(Path(tmp_dir.name).iterdir())

    assert len(list_dir) == 8

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

    assert len(list_dir) == 8

    expected = {
        "loads.dat",
        "initialtemperature.dat",
        "case.dat",
        "adiabat.dat",
        "mesh.dat",
        "initialstress.dat",
        "materials.dat",
        "hidrationprop.dat",
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
