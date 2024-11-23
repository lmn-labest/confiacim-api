from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from confiacim_api.errors import (
    LoadsFileEmptyError,
    LoadsFileNotFoundInZipError,
)
from confiacim_api.models import Case
from confiacim_api.types import TArrayFloat


@dataclass(frozen=True)
class MechanicalLoads:
    t: TArrayFloat
    force: TArrayFloat


@dataclass(frozen=True)
class ThermalLoads:
    t: TArrayFloat
    h: TArrayFloat
    temperature: TArrayFloat


@dataclass(frozen=True)
class LoadsInfos:
    nodalsource: float
    mechanical_loads: MechanicalLoads
    thermal_loads: ThermalLoads


def extract_loads_infos(file_str: str) -> LoadsInfos:
    """
    Extrai o valores do loads desejados

    Parameters:
        file_str: Conteudo do arquivo de `loads.dat` no formato de `str`.

    Returns:
        Retorna o valor dos loads.
    """

    if file_str == "":
        raise LoadsFileEmptyError("Empty loads file.")

    lines_generator = iter(file_str.split("\n"))

    for line in lines_generator:

        if "end" in line:
            continue

        elif "nodalsources" in line:
            words = next(lines_generator).split()
            nodalsources = float(words[1])
            next(lines_generator)

        elif "loads" in line and "nodalloads" not in line and "nodalthermloads" not in line:
            words = next(lines_generator).split()
            tmp1: list[tuple[float, float]] = []
            for _ in range(int(words[-1])):
                words = next(lines_generator).split()
                tmp1.append((float(words[0]), float(words[1])))

            mechanical_loads = MechanicalLoads(
                t=tuple(x[0] for x in tmp1),
                force=tuple(x[1] for x in tmp1),
            )

            words = next(lines_generator).split()
            tmp2: list[tuple[float, float, float]] = []
            for _ in range(int(words[-1])):
                words = next(lines_generator).split()
                tmp2.append((float(words[0]), float(words[1]), float(words[2])))

            therm_loads = ThermalLoads(
                t=tuple(x[0] for x in tmp2),
                h=tuple(x[1] for x in tmp2),
                temperature=tuple(x[2] for x in tmp2),
            )

            next(lines_generator)

    return LoadsInfos(
        nodalsource=nodalsources,
        mechanical_loads=mechanical_loads,
        thermal_loads=therm_loads,
    )


def read_loads_file(path_file: Path) -> LoadsInfos:
    """
    Lê o arquivo de loads e extrai os valores desejados

    Parameters:
        path_file: Lê o arquivos `loads.dat`.

    Returns:
        Retorna o valor dos loads.
    """
    return extract_loads_infos(path_file.read_text())


def extract_loads_infos_from_blob(case: Case) -> LoadsInfos:
    """
    Extrai as informações dos loads diretamentamente do blob salvo no
    DB.

    Parameters:
        case: Caso

    Returns:
        LoadsInfos: Retorna o valor dos loads.
    """

    with ZipFile(BytesIO(case.base_file), "r") as zip_ref:
        try:
            with zip_ref.open("loads.dat") as fp:
                loads_infos = extract_loads_infos(fp.read().decode())
        except KeyError as e:
            raise LoadsFileNotFoundInZipError("Loads file not found in zip.") from e

    return loads_infos
