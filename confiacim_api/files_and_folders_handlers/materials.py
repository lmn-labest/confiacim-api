from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from confiacim_api.errors import (
    MaterialsFileEmptyError,
    MaterialsFileNotFoundInZipError,
    MaterialsFileValueError,
)
from confiacim_api.models import Case


class MaterialsFileLinesIndex(Enum):
    CEMENT_LINE = 3
    FORMATION_LINE = 4


class MaterialsFileColumnsIndex(Enum):
    MAT_NUMBER = 0
    E_COEF = 2
    POISSON_COEF = 3
    THERMAL_EXPANSION_COEF = 4
    THERMAL_CONDUTIVITY_COEF = 7
    VOLUMETRIC_HEAT_CAPACITY_COEF = 8
    FRICTION_ANGLE_COEF = 13
    COHESION_COEF = 14


@dataclass(frozen=True)
class MaterialsInfos:
    E_c: float
    poisson_c: float
    thermal_expansion_c: float
    thermal_conductivity_c: float
    volumetric_heat_capacity_c: float
    friction_angle_c: float
    cohesion_c: float

    E_f: float
    poisson_f: float
    thermal_expansion_f: float
    thermal_conductivity_f: float
    volumetric_heat_capacity_f: float


def extract_materials_infos(file_str: str) -> MaterialsInfos:
    """
    Extrai o valores do materias desejados

    Parameters:
        file_str: Conteudo do arquivo de `materials.dat` no formato de `str`.

    Returns:
        Retorna o valor dos materiais.
    """

    lines = file_str.split("\n")

    if lines == [""]:
        raise MaterialsFileEmptyError("Empty materials file.")

    tmp_dict = {}

    for lin in lines:

        if "end materials" in lin:
            break

        if "materials" in lin:
            continue

        words = lin.split()

        try:
            mat_number = int(words[MaterialsFileColumnsIndex.MAT_NUMBER.value])
        except ValueError as e:
            raise MaterialsFileValueError(f"Invalid material number: {e}") from e

        if mat_number == 3:
            try:
                tmp_dict["E_c"] = float(words[MaterialsFileColumnsIndex.E_COEF.value])
                tmp_dict["poisson_c"] = float(words[MaterialsFileColumnsIndex.POISSON_COEF.value])
                tmp_dict["thermal_expansion_c"] = float(words[MaterialsFileColumnsIndex.THERMAL_EXPANSION_COEF.value])
                tmp_dict["thermal_conductivity_c"] = float(
                    words[MaterialsFileColumnsIndex.THERMAL_CONDUTIVITY_COEF.value]
                )
                tmp_dict["volumetric_heat_capacity_c"] = float(
                    words[MaterialsFileColumnsIndex.VOLUMETRIC_HEAT_CAPACITY_COEF.value]
                )
                tmp_dict["friction_angle_c"] = float(words[MaterialsFileColumnsIndex.FRICTION_ANGLE_COEF.value])
                tmp_dict["cohesion_c"] = float(words[MaterialsFileColumnsIndex.COHESION_COEF.value])
            except ValueError as e:
                raise MaterialsFileValueError(f"Invalid prop value in material {mat_number}: {e}") from e

        elif mat_number == 4:
            try:
                tmp_dict["E_f"] = float(words[MaterialsFileColumnsIndex.E_COEF.value])
                tmp_dict["poisson_f"] = float(words[MaterialsFileColumnsIndex.POISSON_COEF.value])
                tmp_dict["thermal_expansion_f"] = float(words[MaterialsFileColumnsIndex.THERMAL_EXPANSION_COEF.value])
                tmp_dict["thermal_conductivity_f"] = float(
                    words[MaterialsFileColumnsIndex.THERMAL_CONDUTIVITY_COEF.value]
                )
                tmp_dict["volumetric_heat_capacity_f"] = float(
                    words[MaterialsFileColumnsIndex.VOLUMETRIC_HEAT_CAPACITY_COEF.value]
                )
            except ValueError as e:
                raise MaterialsFileValueError(f"Invalid prop value in material {mat_number}: {e}") from e

    return MaterialsInfos(**tmp_dict)


def read_materials_file(path_file: Path) -> MaterialsInfos:
    """
    Lê o arquivo de materiais e extrai os valores desejados

    Parameters:
        path_file: Lê o arquivos `materials.dat`.

    Returns:
        Retorna o valor dos materiais.
    """
    return extract_materials_infos(path_file.read_text())


def extract_materials_infos_from_blob(case: Case) -> MaterialsInfos:
    """
    Extrai as informações dos materiais diretamentamente do blob salvo no
    DB.

    Parameters:
        case: Caso

    Returns:
        MaterialsInfos: Retorna o valor dos materiais.
    """

    with ZipFile(BytesIO(case.base_file), "r") as zip_ref:
        try:
            with zip_ref.open("materials.dat") as fp:
                mat_infos = extract_materials_infos(fp.read().decode())
        except KeyError as e:
            raise MaterialsFileNotFoundInZipError("Materials file not found in zip.") from e

    return mat_infos
