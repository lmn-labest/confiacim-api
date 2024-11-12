from io import BytesIO

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from confiacim_api.app import app
from confiacim_api.errors import (
    MaterialsFileEmptyError,
    MaterialsFileNotFoundInZipError,
)
from confiacim_api.models import Case, User

ROUTE_VIEW_NAME = "case_create"


@pytest.fixture(scope="module")
def payload():
    return {"tag": "case_1"}


@pytest.mark.integration
def test_positive_create(client_auth: TestClient, session, user: User, payload):

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME),
            data=payload | {"description": "Any description you want"},
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_201_CREATED

    case_from_db = session.scalars(select(Case)).first()

    assert case_from_db.id
    assert case_from_db.tag == payload["tag"]
    assert case_from_db.user == user
    assert case_from_db.description == "Any description you want"

    assert case_from_db.materials.E_c == pytest.approx(1.096e10)
    assert case_from_db.materials.poisson_c == pytest.approx(0.228)
    assert case_from_db.materials.thermal_expansion_c == pytest.approx(1.0e-05)
    assert case_from_db.materials.thermal_conductivity_c == pytest.approx(1.75)
    assert case_from_db.materials.volumetric_heat_capacity_c == pytest.approx(1.869e06)
    assert case_from_db.materials.friction_angle_c == pytest.approx(1.4e01)
    assert case_from_db.materials.cohesion_c == pytest.approx(1.817e07)

    assert case_from_db.materials.E_f == pytest.approx(3.792e10)
    assert case_from_db.materials.poisson_f == pytest.approx(0.21)
    assert case_from_db.materials.thermal_expansion_f == pytest.approx(4.14e-05)
    assert case_from_db.materials.thermal_conductivity_f == pytest.approx(6.006e00)
    assert case_from_db.materials.volumetric_heat_capacity_f == pytest.approx(1.929e06)

    body = resp.json()

    assert body["id"] == case_from_db.id
    assert body["tag"] == case_from_db.tag
    assert body["user"] == case_from_db.user.id
    assert body["description"] == case_from_db.description

    assert body["materials"]["E_c"] == case_from_db.materials.E_c
    assert body["materials"]["poisson_c"] == case_from_db.materials.poisson_c
    assert body["materials"]["thermal_expansion_c"] == case_from_db.materials.thermal_expansion_c
    assert body["materials"]["thermal_conductivity_c"] == case_from_db.materials.thermal_conductivity_c
    assert body["materials"]["volumetric_heat_capacity_c"] == case_from_db.materials.volumetric_heat_capacity_c
    assert body["materials"]["friction_angle_c"] == case_from_db.materials.friction_angle_c
    assert body["materials"]["cohesion_c"] == case_from_db.materials.cohesion_c

    assert body["materials"]["E_f"] == case_from_db.materials.E_f
    assert body["materials"]["poisson_f"] == case_from_db.materials.poisson_f
    assert body["materials"]["thermal_expansion_f"] == case_from_db.materials.thermal_expansion_f
    assert body["materials"]["thermal_conductivity_f"] == case_from_db.materials.thermal_conductivity_f
    assert body["materials"]["volumetric_heat_capacity_f"] == case_from_db.materials.volumetric_heat_capacity_f


@pytest.mark.integration
def test_positive_create_description_is_optional(
    client_auth: TestClient,
    session,
    user: User,
    payload,
):

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME),
            data=payload,
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_201_CREATED

    case_from_db = session.scalars(select(Case)).first()

    assert case_from_db.id
    assert case_from_db.tag == payload["tag"]
    assert case_from_db.user == user
    assert case_from_db.description is None

    body = resp.json()

    assert body["id"] == case_from_db.id
    assert body["tag"] == case_from_db.tag
    assert body["user"] == case_from_db.user.id
    assert body["description"] is None


@pytest.mark.integration
def test_negative_create_missing_tag(client_auth: TestClient, session, zip_file_fake: BytesIO):

    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME),
        data={},
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    case_db = session.scalars(select(Case)).first()

    assert not case_db

    body = resp.json()

    assert body["detail"][0]["loc"] == ["body", "tag"]
    assert body["detail"][0]["msg"] == "Field required"
    assert body["detail"][0]["type"] == "missing"


@pytest.mark.integration
def test_negative_create_tag_must_be_lt_30(
    client_auth: TestClient,
    session,
    zip_file_fake: BytesIO,
):

    payload = {"tag": "s" * 31}

    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME),
        data=payload,
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    case_db = session.scalars(select(Case)).first()

    assert not case_db

    body = resp.json()

    assert body["detail"][0]["loc"] == ["body", "tag"]
    assert body["detail"][0]["msg"] == "String should have at most 30 characters"
    assert body["detail"][0]["type"] == "string_too_long"


@pytest.mark.integration
def test_negative_create_tag_must_be_gt_3(
    client_auth: TestClient,
    session,
    zip_file_fake: BytesIO,
):

    payload = {"tag": "s" * 2}

    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME),
        data=payload,
        files={"case_file": zip_file_fake},
    )
    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    case_db = session.scalars(select(Case)).first()

    assert not case_db

    body = resp.json()

    assert body["detail"][0]["loc"] == ["body", "tag"]
    assert body["detail"][0]["msg"] == "String should have at least 3 characters"
    assert body["detail"][0]["type"] == "string_too_short"


@pytest.mark.integration
def test_negative_create_tag_name_must_be_unique_per_user(
    client_auth: TestClient,
    case: Case,
    zip_file_fake: BytesIO,
):
    payload = {"tag": "case_1"}

    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME),
        data=payload,
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    assert resp.json() == {"detail": "Case Tag name shoud be unique per user."}


@pytest.mark.integration
def test_positive_create_two_user_can_have_the_same_tag_name(
    client: TestClient,
    session,
    case: Case,
    other_user_token: str,
):
    payload = {"tag": "case_1"}

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client.post(
            app.url_path_for(ROUTE_VIEW_NAME),
            data=payload,
            files={"case_file": fp},
            headers={"Authorization": f"Bearer {other_user_token}"},
        )

    assert resp.status_code == status.HTTP_201_CREATED
    assert session.scalar(select(func.count()).select_from(Case)) == 2


@pytest.mark.integration
def test_negative_file_problem_case_zipfile_without_materials(
    session,
    client_auth: TestClient,
    payload,
):

    with open("tests/fixtures/case_without_materials.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME),
            data=payload,
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    assert resp.json() == {"detail": "Materials file not found in zip."}


@pytest.mark.integration
def test_negative_file_problem_raise_materials_file_not_found_in_zipfile_error(
    session,
    client_auth: TestClient,
    mocker,
    payload,
):

    mocker.patch(
        "confiacim_api.routers.case.extract_materials_infos_from_blob",
        side_effect=MaterialsFileNotFoundInZipError("Materials file not found in zip."),
    )

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME),
            data=payload,
            files={"case_file": fp},
        )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "Materials file not found in zip."}


@pytest.mark.integration
def test_negative_file_problem_upload_case_must_be_a_zipfile(
    client_auth: TestClient,
    payload,
    mocker,
    zip_file_fake: BytesIO,
):
    is_zipfile_mocker = mocker.patch(
        "confiacim_api.routers.case.file_case_is_zipfile",
        return_value=False,
    )

    resp = client_auth.post(
        app.url_path_for(ROUTE_VIEW_NAME),
        data=payload,
        files={"case_file": zip_file_fake},
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    is_zipfile_mocker.assert_called_once()

    assert resp.json() == {"detail": "The file must be a zip file."}


@pytest.mark.integration
def test_negative_file_problem_raise_empty_materials_file(
    session,
    client_auth: TestClient,
    mocker,
    payload,
):

    mocker.patch(
        "confiacim_api.files_and_folders_handlers.extract_materials_infos",
        side_effect=MaterialsFileEmptyError("Empty materials file."),
    )

    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        resp = client_auth.post(
            app.url_path_for(ROUTE_VIEW_NAME),
            data=payload,
            files={"case_file": fp},
        )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert resp.json() == {"detail": "Empty materials file."}


@pytest.mark.integration
def test_negative_create_case_must_have_token(client: TestClient):
    resp = client.get(app.url_path_for(ROUTE_VIEW_NAME))

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
