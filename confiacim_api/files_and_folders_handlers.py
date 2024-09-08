from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO, Optional
from uuid import UUID
from zipfile import ZipFile

from confiacim.tencim.deterministic import new_case_with_until_the_step

from confiacim_api.errors import (
    MaterialsFileEmptyError,
    MaterialsFileValueError,
)
from confiacim_api.logger import logger
from confiacim_api.models import Case

NO_CLIP_RC = "nocliprc"


class MaterialsFileLinesIndex(Enum):
    CEMENT_LINE = 3
    FORMATION_LINE = 4


class MaterialsFileColumnsIndex(Enum):
    MAT_NUMBER = 0
    E_COEF = 2
    POISSON_COEF = 3


@dataclass(frozen=True)
class MaterialsInfos:
    E_c: float
    poisson_c: float
    E_f: float
    poisson_f: float


def temporary_simulation_folder(origin_dir: Path) -> TemporaryDirectory:
    """
    Gera o diretório temporátio base para a simulação.

    Parameters:
        origin_dir: Diretório base

    Returns:
        Caminho completo do diretório temporário.
    """
    return TemporaryDirectory(dir=origin_dir)


def unzip_file(file: BinaryIO, temp_folder: TemporaryDirectory):
    """
    Desempacota um arquivo zip para para uma pasta específica.

    Parameters:
        file: Arquivo zip
        temp_folder: Caminho base
    """

    path = Path(temp_folder.name)
    with ZipFile(file, "r") as zip_ref:
        zip_ref.extractall(path)


def clean_temporary_simulation_folder(dir: TemporaryDirectory):
    """Limpa o diretorio temporario"""
    dir.cleanup()


def unzip_tencim_case(case: Case, tmp_dir: TemporaryDirectory):
    """
    Unzip o caso da simulação do Tencim do blob salvo no banco de Dados

    Parameters:
        case: Caso (ORM)
        tmp_dir: Diretorio temporario
    """
    file_like = BytesIO(case.base_file)
    unzip_file(file_like, tmp_dir)


def add_nocliprc_macro(case_file_str: str) -> str:
    """
    Add a macro nocliprc no conteudo arquivo case.dat

    Parameters:
        case_file_str: Conteudo do arquivo case.dat

    Returns:
        Returna o conteudo com a macro nocliprc.
    """
    if NO_CLIP_RC in case_file_str:
        return case_file_str

    return case_file_str.replace("end mesh\n", f"end mesh\n{NO_CLIP_RC}\n")


def rm_nocliprc_macro(case_file_str: str) -> str:
    """
    Add a macro nocliprc no conteudo arquivo case.dat

    Parameters:
        case_file_str: Conteudo do arquivo case.dat

    Returns:
        Returna o conteudo com a macro nocliprc.
    """
    if NO_CLIP_RC not in case_file_str:
        return case_file_str

    return case_file_str.replace(f"{NO_CLIP_RC}\n", "")


def rm_setpnode_and_setptime(case_file_str: str) -> str:
    """
    Remove as macros setpnode e setptime do conteudo arquivo case.dat

    Parameters:
        case_file_str: Conteudo do arquivo case.dat

    Returns:
        Returna o conteudo com as macros removidas setpnode e setptime.
    """

    # TODO: transforma setpnode e setptime é uma constante
    return "\n".join(line for line in case_file_str.split("\n") if "setpnode" not in line and "setptime" not in line)


def rewrite_case_file(
    *,
    task_id: UUID,
    case_path: Path,
    rc_limit: bool = False,
    setpnode_and_setptime: bool = True,
    last_step: Optional[int] = None,
):
    """
    Reescreve o arquivo case.dat

    Parameters:
        task_id: id da task celerey
        case_path: caminho do arquivo case.dat
        rc_limit: add a macro nocliprc.
        setpnode_and_time: retira as macros setpnode e setptime
    """

    with open(case_path, encoding="utf-8") as fp:
        new_file_case = fp.read()

    is_new_file = False

    if rc_limit:
        logger.info(f"Task {task_id} - Removing norcclip ...")
        new_file_case = rm_nocliprc_macro(new_file_case)
        is_new_file = True
    else:
        logger.info(f"Task {task_id} - Add norcclip ...")
        new_file_case = add_nocliprc_macro(new_file_case)
        is_new_file = True

    if setpnode_and_setptime:
        logger.info(f"Task {task_id} - Removing setpnode and setptime ...")
        new_file_case = rm_setpnode_and_setptime(new_file_case)
        is_new_file = True

    if last_step:
        logger.info(f"Task {task_id} - Novo loop de tempo até passo {last_step} ...")
        new_file_case = new_time_loop(new_file_case, last_step)
        is_new_file = True

    if is_new_file:
        logger.debug(f"Task {task_id} - Writing the new file in disk ...")
        with open(case_path, mode="w", encoding="utf-8") as fp:
            fp.write(new_file_case)


def new_time_loop(case_file_str: str, last_step: int) -> str:
    """
    Gera case truncado no new_last_step

    Danger:
        Caso `new_last_step` seja maior que o número de passos do caso original
        será mantido o valor inicial. Não será criado mais blocos `loop-next` do `tencim`.

    Parameters:
        case_data_str: Conteudo do Arquivo de `case.dat` no formato de `str`.
        new_last_step: Novo ultimo passo de tempo.

    Returns:
        Retorna no novo conteudo do arquivo `case.dat`.
    """
    return new_case_with_until_the_step(case_data_str=case_file_str, new_last_step=last_step)


def extract_materials_infos(file_str: str) -> MaterialsInfos:
    """
    Extrai o valores do materias desejados

    Parameters:
        case_data_str: Conteudo do arquivo de `materials.dat` no formato de `str`.

    Returns:
        Retorna o valor dos materiais.
    """

    lines = file_str.split("\n")

    if lines == [""]:
        raise MaterialsFileEmptyError("Empty materials file.")

    tmp_dict = {}

    for lin in lines:

        if "materials" == lin:
            continue

        if "end materials" == lin:
            break

        words = lin.split()

        try:
            mat_number = int(words[MaterialsFileColumnsIndex.MAT_NUMBER.value])
        except ValueError as e:
            raise MaterialsFileValueError(f"Invalid material number: {e}") from e

        if mat_number == 3:
            try:
                tmp_dict["E_c"] = float(words[MaterialsFileColumnsIndex.E_COEF.value])
                tmp_dict["poisson_c"] = float(words[MaterialsFileColumnsIndex.POISSON_COEF.value])
            except ValueError as e:
                raise MaterialsFileValueError(f"Invalid prop value in material {mat_number}: {e}") from e

        elif mat_number == 4:
            try:
                tmp_dict["E_f"] = float(words[MaterialsFileColumnsIndex.E_COEF.value])
                tmp_dict["poisson_f"] = float(words[MaterialsFileColumnsIndex.POISSON_COEF.value])
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
        with zip_ref.open("materials.dat") as fp:
            mat_infos = extract_materials_infos(fp.read().decode())

    return mat_infos
