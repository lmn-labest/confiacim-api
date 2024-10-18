from pathlib import Path
from uuid import UUID

from confiacim_api.files_and_folders_handlers import extract_materials_infos
from confiacim_api.logger import logger

PROP_MAT_POSITION = {
    # CEMENT
    "E_c": 2,
    "poisson_c": 3,
    "thermal_expansion_c": 4,
    "thermal_conductivity_c": 7,
    "volumetric_heat_capacity_c": 8,
    "friction_angle_c": 13,
    "cohesion_c": 14,
    # formation
    "E_f": 2,
    "poisson_f": 3,
    "thermal_expansion_f": 4,
    "thermal_conductivity_f": 7,
    "volumetric_heat_capacity_f": 8,
}

PROP_CEMENT = (
    "E_c,poisson_c,thermal_expansion_c,thermal_conductivity_c,volumetric_heat_capacity_c,friction_angle_c,cohesion_c"
)
PROP_FORMANTION = "E_f,poisson_f,thermal_expansion_f,thermal_conductivity_f,volumetric_heat_capacity_f"
LINE_CEMENT_MATERIAL = 3
LINE_FORMATION_MATERIAL = 4


def generate_materials_template(materials_str: str, mat_props: dict[str, float]) -> str:
    """
    Gera o template jinja do conteudo materials.dat. As propriedades que serão add
    estão definidads no dicionario mat_props. O template gerado é da versão unitaria
    do `FORM `.

    Parameters:
        materials_str: Conteudo do arquivo de `materials.dat` no formato de `str`
        mat_props: Propriedades que serão dinamicas no template

    Returns:
        Retorna o template jinja
    """
    lines = materials_str.split("\n")

    lines[1] = lines[1].strip()
    lines[2] = lines[2].strip()

    cement = lines[LINE_CEMENT_MATERIAL].split()
    formation = lines[LINE_FORMATION_MATERIAL].split()

    for prop in PROP_CEMENT.split(","):
        if mean := mat_props.get(prop):
            cement[PROP_MAT_POSITION[prop]] = f'{{{{ "%.16e"|format({prop} * {mean}) }}}}'

    for prop in PROP_FORMANTION.split(","):
        if mean := mat_props.get(prop):
            formation[PROP_MAT_POSITION[prop]] = f'{{{{ "%.16e"|format({prop} * {mean}) }}}}'

    lines[LINE_CEMENT_MATERIAL] = " ".join(cement)
    lines[LINE_FORMATION_MATERIAL] = " ".join(formation)

    return "\n".join(lines)


def generate_templates(task_id: UUID | None, base_folder: Path, config: dict):
    """
    Gera os templates jinja.

    Parameters:
        task_id: ID da task do celery
        base_folder: Caminho do diretorio base
        config: Configuração do FORM

    """

    materials = base_folder / "materials.dat"

    base_folder_template = base_folder / "templates"
    base_folder_template.mkdir(exist_ok=True)

    logger.info(f"Task {task_id} - Generating materials.jinja ...")
    variables_name = tuple(var["name"] for var in config["variables"])

    materilas_str = materials.read_text()
    mat_infos = extract_materials_infos(materilas_str)
    mat_props = {name: getattr(mat_infos, name) for name in variables_name}
    jinja_str = generate_materials_template(
        materilas_str,
        mat_props,
    )
    materials_jinja = base_folder_template / "materials.jinja"
    materials_jinja.write_text(jinja_str)

    logger.info(f"Task {task_id} - Generated.")
