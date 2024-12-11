import pytest
from fastapi import status
from fastapi.testclient import TestClient

from confiacim_api.app import app
from confiacim_api.models import TencimResult

ROUTE_NAME = "tencim_result_retrieve_csv"
CSV_FILE = b"istep,t,rc_rankine,mohr_coulomb_rc\r\n1,1.0,100.0,100.0\r\n2,2.0,90.0,80.0\r\n3,3.0,10.0,30.0\r\n"


@pytest.mark.integration
def test_positive_csv_download(client_auth: TestClient, tencim_results: TencimResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=tencim_results.case_id,
        result_id=tencim_results.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_200_OK

    assert resp.headers["content-disposition"] == f"attachment;filename={tencim_results.case.tag}.csv"
    assert resp.headers["content-type"] == "text/csv; charset=utf-8"
    assert resp.content == CSV_FILE


@pytest.mark.integration
def test_negative_csv_download_result_not_found(client_auth: TestClient, tencim_results: TencimResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=tencim_results.case_id,
        result_id=404,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_csv_download_case_not_found(client_auth: TestClient, tencim_results: TencimResult):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=404,
        result_id=tencim_results.id,
    )

    resp = client_auth.get(url)

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_csv_download_user_can_download_results_only_their_own_cases(
    client: TestClient,
    tencim_results: TencimResult,
    other_user_token: str,
):

    url = app.url_path_for(
        ROUTE_NAME,
        case_id=tencim_results.case.id,
        result_id=tencim_results.id,
    )

    resp = client.get(
        url,
        headers={"Authorization": f"Bearer {other_user_token}"},
    )

    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Result/Case not found"


@pytest.mark.integration
def test_negative_csv_download_result_must_have_token(client: TestClient):

    url = app.url_path_for(ROUTE_NAME, case_id=1, result_id=1)

    resp = client.get(url)

    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    assert resp.json() == {"detail": "Not authenticated"}
