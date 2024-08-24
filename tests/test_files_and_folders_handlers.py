import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest
from sqlalchemy import select

from confiacim_api.files_and_folders_handlers import (
    add_nocliprc_macro,
    clean_temporary_simulation_folder,
    rewrite_case_file,
    temporary_simulation_folder,
    unzip_file,
    unzip_tencim_case,
)
from confiacim_api.models import Case


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
def test_case_file_with_nocliprc_macro():

    with open("tests/fixtures/case.dat") as fp:
        case_file = fp.read()

    new_file = add_nocliprc_macro(case_file)

    assert "end mesh\nnocliprc\n" in new_file


@pytest.mark.unit
def test_case_file_must_have_only_one_nocliprc_macro():

    with open("tests/fixtures/case_nocliprc.dat") as fp:
        case_file = fp.read()

    assert case_file.count("nocliprc") == 1

    new_file = add_nocliprc_macro(case_file)

    assert new_file.count("nocliprc") == 1


@pytest.mark.integration
def test_rewrite_case_file(tmp_path):

    shutil.copy2("tests/fixtures/case.dat", tmp_path)

    case_path = tmp_path / "case.dat"

    assert "nocliprc" not in case_path.read_text()

    rewrite_case_file(task_id=uuid4(), case_path=case_path, rc_limit=True)

    assert case_path.read_text().count("nocliprc") == 1


@pytest.mark.integration
def test_not_rewrite_case_file(tmp_path):

    shutil.copy2("tests/fixtures/case.dat", tmp_path)

    case_path = tmp_path / "case.dat"

    assert "nocliprc" not in case_path.read_text()

    rewrite_case_file(task_id=uuid4(), case_path=case_path, rc_limit=False)

    assert "nocliprc" not in case_path.read_text()
