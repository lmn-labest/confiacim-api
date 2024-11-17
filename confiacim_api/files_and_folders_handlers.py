from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from itertools import chain
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO, Optional
from uuid import UUID
from zipfile import ZIP_DEFLATED, ZipFile

from confiacim.tencim.deterministic import new_case_with_until_the_step
from sqlalchemy.orm import Session

from confiacim_api.errors import (
    LoadsFileEmptyError,
    MaterialsFileEmptyError,
    MaterialsFileNotFoundInZipError,
    MaterialsFileValueError,
)
from confiacim_api.logger import logger
from confiacim_api.models import Case, FormResult

NO_CLIP_RC = "nocliprc"


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


@dataclass(frozen=True)
class MechanicalLoads:
    istep: tuple[int, ...]
    force: tuple[float, ...]


@dataclass(frozen=True)
class ThermalLoads:
    istep: tuple[int, ...]
    h: tuple[float, ...]
    temperature: tuple[float, ...]


@dataclass(frozen=True)
class LoadsInfos:
    nodalsource: float
    mechanical_loads: MechanicalLoads
    thermal_loads: ThermalLoads


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

    # TODO: transforma setpnode e setptime em uma constante
    return "\n".join(line for line in case_file_str.split("\n") if "setpnode" not in line and "setptime" not in line)


def rewrite_case_file(
    *,
    task_id: UUID,
    case_path: Path,
    rc_limit: bool = False,
    setpnode_and_setptime: bool = True,
    critical_point: Optional[int] = None,
):
    """
    Reescreve o arquivo case.dat

    Parameters:
        task_id: id da task celerey
        case_path: caminho do arquivo case.dat
        rc_limit: add a macro nocliprc.
        setpnode_and_setptime: retira as macros setpnode e setptime
    """

    with open(case_path, encoding="utf-8") as fp:
        new_file_case = fp.read()

    new_file_case = remove_tab_and_unnecessary_spaces(new_file_case)

    if rc_limit:
        logger.info(f"Task {task_id} - Removing norcclip ...")
        new_file_case = rm_nocliprc_macro(new_file_case)
    else:
        logger.info(f"Task {task_id} - Add norcclip ...")
        new_file_case = add_nocliprc_macro(new_file_case)

    if setpnode_and_setptime:
        logger.info(f"Task {task_id} - Removing setpnode and setptime ...")
        new_file_case = rm_setpnode_and_setptime(new_file_case)

    if critical_point:
        logger.info(f"Task {task_id} - Novo loop de tempo até passo {critical_point} ...")
        new_file_case = new_time_loop(new_file_case, critical_point)

    logger.debug(f"Task {task_id} - Writing the new file in disk ...")
    with open(case_path, mode="w", encoding="utf-8") as fp:
        fp.write(new_file_case)


def remove_tab_and_unnecessary_spaces(file_case_str: str) -> str:
    """
    Remove espações e tabulações desncessarias do arquivo

    Parameters:
        file_case_str: Conteudo do arquivo no formato de `str`.

    Returns:
        Retorna o conteudo file_case_str
    """
    new_lines = [line.strip() for line in file_case_str.split("\n")]
    new_file_case = "\n".join(new_lines)
    return new_file_case.replace("\t", "")


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


def zip_generated_form_case(path_folder: Path):
    """
    Gera um zip com os arquivos da pasta.

    Parameters:
        path_folder: Caminho para a pasta com o conteudo
    """

    with ZipFile(path_folder / "tmp_case_form.zip", "w", ZIP_DEFLATED) as zipf:
        files = chain(
            path_folder.rglob("*.dat"),
            path_folder.rglob("*.yml"),
            path_folder.rglob("*.jinja"),
        )
        for file in files:
            zipf.write(file, file.relative_to(path_folder))


def save_zip_in_db(session: Session, zip_path: Path, form_result: FormResult):
    """
    Salva zip no DB.

    Parameters:
        session: Secção aberta com o banco
        zip_path: Caminho para o arquivo zipado
        form_result: Resultado do `FORM`
    """

    with open(zip_path, "rb") as zip_ref:
        form_result.generated_case_files = zip_ref.read()

    session.add(form_result)
    session.commit()


def save_generated_form_files(session: Session, path_folder: Path, form_result: FormResult):
    """
    Salva os arquivos do caso `FORM` no DB.

    Parameters:
        session: Secção aberta com o banco
        path_folder: Caminho para o arquivo zipado
        form_result: Resultado do `FORM`
    """

    zip_path = path_folder / "tmp_case_form.zip"
    zip_generated_form_case(path_folder)
    save_zip_in_db(session, zip_path, form_result)
    zip_path.unlink()


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
            tmp1: list[tuple[int, float]] = []
            for _ in range(int(words[-1])):
                words = next(lines_generator).split()
                tmp1.append((int(words[0]), float(words[1])))

            mechanical_loads = MechanicalLoads(
                istep=tuple(x[0] for x in tmp1),
                force=tuple(x[1] for x in tmp1),
            )

            words = next(lines_generator).split()
            tmp2: list[tuple[int, float, float]] = []
            for _ in range(int(words[-1])):
                words = next(lines_generator).split()
                tmp2.append((int(words[0]), float(words[1]), float(words[2])))

            therm_loads = ThermalLoads(
                istep=tuple(x[0] for x in tmp2),
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
