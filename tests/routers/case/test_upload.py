from io import BytesIO

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.errors import (
    MaterialsFileEmptyError,
    MaterialsFileNotFoundInZipError,
    MaterialsFileValueError,
)
from confiacim_api.files_and_folders_handlers import MaterialsInfos
from confiacim_api.models import Case, MaterialsBaseCaseAverageProps

ROUTE_VIEW_NAME = "upload_case_file"


@pytest.mark.integration
def test_upload_case(
    session,
    client_auth: TestClient,
    case: Case,
    mocker,
    zip_file_fake: BytesIO,
):
    is_zipfile_mocker = mocker.patch(
        "confiacim_api.routers.case.file_case_is_zipfile",
        return_value=True,
    )

    extract_materials_infos_from_blob_mocker = mocker.patch(
        "confiacim_api.routers.case.extract_materials_infos_from_blob",
        return_value=MaterialsInfos(
            E_c=1.0,
            poisson_c=0.2,
            thermal_expansion_c=0.3,
            thermal_conductivity_c=0.4,
            volumetric_heat_capacity_c=0.5,
            friction_angle_c=0.6,
            cohesion_c=0.7,
            #
            E_f=1.0,
            poisson_f=0.1,
            thermal_expansion_f=0.2,
            thermal_conductivity_f=0.3,
            volumetric_heat_capacity_f=0.4,
        ),
    )

    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_200_OK

    is_zipfile_mocker.assert_called_once()
    extract_materials_infos_from_blob_mocker.assert_called_once()

    assert resp.json() == {"detail": "File upload success."}

    case_from_db = session.get(Case, case.id)

    assert case_from_db.materials.E_c == pytest.approx(1.0)
    assert case_from_db.materials.poisson_c == pytest.approx(0.2)
    assert case_from_db.materials.thermal_expansion_c == pytest.approx(0.3)
    assert case_from_db.materials.thermal_conductivity_c == pytest.approx(0.4)
    assert case_from_db.materials.volumetric_heat_capacity_c == pytest.approx(0.5)
    assert case_from_db.materials.friction_angle_c == pytest.approx(0.6)
    assert case_from_db.materials.cohesion_c == pytest.approx(0.7)

    assert case_from_db.materials.E_f == pytest.approx(1.0)
    assert case_from_db.materials.poisson_f == pytest.approx(0.1)
    assert case_from_db.materials.thermal_expansion_f == pytest.approx(0.2)
    assert case_from_db.materials.thermal_conductivity_f == pytest.approx(0.3)
    assert case_from_db.materials.volumetric_heat_capacity_f == pytest.approx(0.4)

    assert case_from_db.base_file == b"Fake zip file."


@pytest.mark.integration
def test_upload_case_real_file(
    session,
    client_auth: TestClient,
    case: Case,
):

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {"detail": "File upload success."}

    case_from_db = session.get(Case, case.id)

    assert case_from_db.materials.E_c == pytest.approx(10960000000.0)
    assert case_from_db.materials.E_f == pytest.approx(37920000000.0)
    assert case_from_db.materials.poisson_c == pytest.approx(0.228)
    assert case_from_db.materials.poisson_f == pytest.approx(0.21)


@pytest.mark.integration
def test_upload_case_already_have_materials(
    session,
    client_auth: TestClient,
    case: Case,
    materials: MaterialsBaseCaseAverageProps,
):

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {"detail": "File upload success."}

    case_from_db = session.get(Case, case.id)

    assert case_from_db.materials.E_c == pytest.approx(10960000000.0)
    assert case_from_db.materials.E_f == pytest.approx(37920000000.0)
    assert case_from_db.materials.poisson_c == pytest.approx(0.228)
    assert case_from_db.materials.poisson_f == pytest.approx(0.21)


@pytest.mark.integration
def test_negative_case_zipfile_without_materials(
    session,
    client_auth: TestClient,
    case: Case,
):

    with open("tests/fixtures/case_without_materials.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    assert resp.json() == {"detail": "Materials file not found in zip."}


@pytest.mark.integration
def test_negative_upload_case_must_be_a_zipfile(
    client_auth: TestClient,
    case: Case,
    mocker,
    zip_file_fake: BytesIO,
):
    is_zipfile_mocker = mocker.patch(
        "confiacim_api.routers.case.file_case_is_zipfile",
        return_value=False,
    )

    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    is_zipfile_mocker.assert_called_once()

    assert resp.json() == {"detail": "The file must be a zip file."}


@pytest.mark.integration
def test_negative_upload_file_raise_materials_file_value_error(
    session,
    client_auth: TestClient,
    mocker,
    case: Case,
):

    mocker.patch(
        "confiacim_api.files_and_folders_handlers.extract_materials_infos",
        side_effect=MaterialsFileValueError("Invalid material number: 1"),
    )

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "Invalid material number: 1"}


@pytest.mark.integration
def test_negative_upload_file_raise_empty_materials_file(
    session,
    client_auth: TestClient,
    mocker,
    case: Case,
):

    mocker.patch(
        "confiacim_api.files_and_folders_handlers.extract_materials_infos",
        side_effect=MaterialsFileEmptyError("Empty materials file."),
    )

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "Empty materials file."}


@pytest.mark.integration
def test_negative_upload_file_raise_materials_file_not_found_in_zip_error(
    session,
    client_auth: TestClient,
    mocker,
    case: Case,
):

    mocker.patch(
        "confiacim_api.routers.case.extract_materials_infos_from_blob",
        side_effect=MaterialsFileNotFoundInZipError("Materials file not found in zip."),
    )

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "Materials file not found in zip."}


@pytest.mark.integration
def test_negative_case_not_found(
    client_auth: TestClient,
    zip_file_fake: BytesIO,
):
    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME, case_id=404),
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found."}


@pytest.mark.integration
def test_negative_user_can_upload_their_own_cases(
    client: TestClient,
    case: Case,
    zip_file_fake: BytesIO,
    other_user_token,
):
    resp = client.post(
        app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id),
        headers={"Authorization": f"Bearer {other_user_token}"},
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND

    assert resp.json() == {"detail": "Case not found."}


@pytest.mark.integration
def test_negative_upload_case_must_have_token(
    client: TestClient,
    case: Case,
):
    resp = client.post(app.url_path_for(ROUTE_VIEW_NAME, case_id=case.id))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
