from fastapi import status

from fastapi.testclient import TestClient

from confiacim_api.app import app

URL = app.url_path_for("index")

def test_index(client:TestClient):

    resp = client.get(URL)

    assert resp.status_code == status.HTTP_200_OK

    assert resp.json() == {"message": "Api do confiacim"}
