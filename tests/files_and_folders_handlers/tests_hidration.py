from pathlib import Path

import pytest

from confiacim_api.errors import hidrationFileEmptyError
from confiacim_api.files_and_folders_handlers.hidration import (
    extract_hidration_infos,
    extract_hidration_infos_from_blob,
    read_hidration_file,
)
from tests.constants import hidration_FILE


@pytest.mark.integration
def test_positive_read_loads():

    path = Path("tests/fixtures/hidrationprop.dat")

    infos = read_hidration_file(path)

    assert infos.E_c.t == (0.0, 0.04, 0.045, 0.08, 0.2, 0.49, 1.0)
    assert infos.E_c.values == (2.200e08, 2.200e08, 8.592e08, 2.429e09, 4.858e09, 8.148e09, 1.190e10)

    assert infos.poisson_c.t == (0.0, 0.04, 0.08, 1.0)
    assert infos.poisson_c.values == (4.900e-01, 4.900e-01, 1.800e-01, 1.800e-01)

    assert infos.cohesion_c.t == (0.0, 0.04, 1.0)
    assert infos.cohesion_c.values == (8.000e05, 8.000e05, 1.970e07)


@pytest.mark.unit
def test_positive_extract_hidration_infos():
    infos = extract_hidration_infos(hidration_FILE)

    assert infos.E_c.t == (0.0, 0.04, 0.045, 0.08, 0.2, 0.49, 1.0)
    assert infos.E_c.values == (2.200e08, 2.200e08, 8.592e08, 2.429e09, 4.858e09, 8.148e09, 1.190e10)

    assert infos.poisson_c.t == (0.0, 0.04, 0.08, 1.0)
    assert infos.poisson_c.values == (4.900e-01, 4.900e-01, 1.800e-01, 1.800e-01)

    assert infos.cohesion_c.t == (0.0, 0.04, 1.0)
    assert infos.cohesion_c.values == (8.000e05, 8.000e05, 1.970e07)


@pytest.mark.unit
def test_negative_extract_extract__hidration_infos_empty_file():

    with pytest.raises(hidrationFileEmptyError, match="Empty hidrationprop file."):
        extract_hidration_infos("")


@pytest.mark.unit
def test_positive_extract_hidration_infos_from_blob(case_with_real_file):

    infos = extract_hidration_infos_from_blob(case_with_real_file)

    assert infos.E_c.t == (0.0, 0.04, 0.045, 0.08, 0.2, 0.49, 1.0)
    assert infos.E_c.values == (2.200e08, 2.200e08, 8.592e08, 2.429e09, 4.858e09, 8.148e09, 1.190e10)

    assert infos.poisson_c.t == (0.0, 0.04, 0.08, 1.0)
    assert infos.poisson_c.values == (4.900e-01, 4.900e-01, 1.800e-01, 1.800e-01)

    assert infos.cohesion_c.t == (0.0, 0.04, 1.0)
    assert infos.cohesion_c.values == (8.000e05, 8.000e05, 1.970e07)


@pytest.mark.unit
def test_extract_hidration_infos_from_blob_without_hidration_file_must_return_none(
    case_with_real_file_without_hidrationprop,
):
    assert extract_hidration_infos_from_blob(case_with_real_file_without_hidrationprop) is None
