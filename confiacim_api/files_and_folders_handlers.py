from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO
from zipfile import ZipFile


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
