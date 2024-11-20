from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from confiacim_api.constants import (
    HIDRATIONPROP_COHESION_C,
    HIDRATIONPROP_E_C,
    HIDRATIONPROP_MAP,
    HIDRATIONPROP_POISSON_C,
)
from confiacim_api.errors import hidrationFileEmptyError
from confiacim_api.logger import logger
from confiacim_api.models import Case


@dataclass(frozen=True)
class TimeSeries:
    t: tuple[float, ...]
    values: tuple[float, ...]


@dataclass(frozen=True)
class HidrationProp:
    E_c: TimeSeries
    poisson_c: TimeSeries
    cohesion_c: TimeSeries


def extract_hidration_infos(file_str: str) -> HidrationProp:
    """
    Extrai as curvas de hidratações desejados

    Parameters:
        file_str: Conteudo do arquivo de `hidrationprop.dat` no formato de `str`.

    Returns:
        Retorna as curvas de hidratações.
    """

    if file_str == "":
        raise hidrationFileEmptyError("Empty hidrationprop file.")

    lines_generator = iter(file_str.split("\n"))

    _ = next(lines_generator)

    tmp = {}

    for line in lines_generator:

        if "end hidrprop" in line:
            break

        _, prop, npoints = map(int, line.split())

        if prop == HIDRATIONPROP_E_C or prop == HIDRATIONPROP_POISSON_C or prop == HIDRATIONPROP_COHESION_C:
            prop_name = HIDRATIONPROP_MAP[prop]
            t, values = [], []
            for _ in range(npoints):
                ti, vi = list(map(float, next(lines_generator).split()))
                t.append(ti)
                values.append(vi)
            tmp[prop_name] = TimeSeries(tuple(t), tuple(values))

        else:
            for _ in range(npoints):
                next(lines_generator)

    return HidrationProp(**tmp)


def read_hidration_file(path_file: Path) -> HidrationProp:
    """
    Lê o arquivo de hidratação e extrai os valores desejados

    Parameters:
        path_file: Lê o arquivos `hidrationprop.dat`.

    Returns:
        Retorna as curvas de hidratações.
    """
    return extract_hidration_infos(path_file.read_text())


def extract_hidration_infos_from_blob(case: Case) -> HidrationProp | None:
    """
    Extrai as informações da hidratação diretamentamente do blob salvo no
    DB.

    Parameters:
        case: Caso

    Returns:
        Retorna as curvas de hidratação.
    """

    with ZipFile(BytesIO(case.base_file), "r") as zip_ref:
        try:
            with zip_ref.open("hidrationprop.dat") as fp:
                logger.info("Hydration files found.")
                infos = extract_hidration_infos(fp.read().decode())
        except KeyError:
            logger.info("No hydration files found.")
            return None
    return infos
