from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO, Optional
from uuid import UUID
from zipfile import ZipFile

from confiacim.tencim.deterministic import new_case_with_until_the_step

from confiacim_api.logger import logger
from confiacim_api.models import Case

NO_CLIP_RC = "nocliprc"


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


def rm_setpnode_and_setptime(case_file_str: str) -> str:
    """
    Remove as macros setpnode e setptime do conteudo arquivo case.dat

    Parameters:
        case_file_str: Conteudo do arquivo case.dat

    Returns:
        Returna o conteudo com as macros removidas setpnode e setptime.
    """

    return "\n".join(line for line in case_file_str.split("\n") if "setpnode" not in line and "setptime" not in line)


def rewrite_case_file(
    *,
    task_id: UUID,
    case_path: Path,
    rc_limit: bool = True,
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
        case_data_str: Conteudo do Arquivo de `case.dat` não forma de `str`.
        new_last_step: Novo ultimo passo de tempo.

    Returns:
        Retorna no novo conteudo do arquivo `case.dat`.
    """
    return new_case_with_until_the_step(case_data_str=case_file_str, new_last_step=last_step)
