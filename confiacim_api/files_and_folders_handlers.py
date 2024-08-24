from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO
from zipfile import ZipFile

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

    return case_file_str.replace("end mesh", f"end mesh\n{NO_CLIP_RC}\n")
