from pathlib import Path

import pytest

from confiacim_api.errors import (
    LoadsFileEmptyError,
    LoadsFileNotFoundInZipError,
)
from confiacim_api.files_and_folders_handlers import (
    extract_loads_infos,
    extract_loads_infos_from_blob,
    read_loads_file,
)
from tests.constants import LOADS_FILE


@pytest.mark.integration
def test_positive_read_loads():

    path = Path("tests/fixtures/loads.dat")

    loads = read_loads_file(path)

    assert loads.nodalsource == 291.639
    assert loads.mechanical_loads.t == (0, 600, 1200, 1800)
    assert loads.mechanical_loads.force == (0, 0, 6.8947e07, 6.8947e07)

    assert loads.thermal_loads.t == (600, 1200, 1800)
    assert loads.thermal_loads.h == (0, 0, 0)
    assert loads.thermal_loads.temperature == (299.073, 299.073, 299.073)


@pytest.mark.unit
def test_positive_extract_loads_infos():

    loads = extract_loads_infos(LOADS_FILE)

    assert loads.nodalsource == 291.639
    assert loads.mechanical_loads.t == (0, 600, 1200, 1800)
    assert loads.mechanical_loads.force == (0, 0, 6.8947e07, 6.8947e07)

    assert loads.thermal_loads.t == (600, 1200, 1800)
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
    assert loads.mechanical_loads.t == (0, 864_000)
    assert loads.mechanical_loads.force == (0, 0)

    assert loads.thermal_loads.t == (864_000,)
    assert loads.thermal_loads.h == (0.0,)
    assert loads.thermal_loads.temperature == (329.362,)


@pytest.mark.unit
def test_negative_extract_loads_infos_from_blob_zipfile_without_loads(case_with_real_file_without_loads):
    with pytest.raises(LoadsFileNotFoundInZipError, match="Loads file not found in zip."):
        extract_loads_infos_from_blob(case_with_real_file_without_loads)
