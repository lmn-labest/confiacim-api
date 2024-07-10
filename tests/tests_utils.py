import pytest

from confiacim_api.utils import file_case_is_zipfile


@pytest.mark.unit
def test_case_file_is_zipfile():
    with open("tests/fixtures/case1.zip", mode="rb") as fp:
        assert file_case_is_zipfile(fp)
        assert fp.tell() == 0


@pytest.mark.unit
def test_negative_case_file_is_zipfile():
    with open("tests/fixtures/case.dat", mode="rb") as fp:
        assert not file_case_is_zipfile(fp)
        assert fp.tell() == 0
