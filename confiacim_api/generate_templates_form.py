from pathlib import Path
from uuid import UUID

from confiacim_api.constants import (
    HIDRATIONPROP,
    HIDRATIONPROP_COHESION_C,
    HIDRATIONPROP_E_C,
    HIDRATIONPROP_MAP,
    HIDRATIONPROP_POISSON_C,
    LINE_CEMENT_MATERIAL,
    LINE_FORMATION_MATERIAL,
    LOADS,
    LOADS_EXTERNAL_TEMPERATURE,
    LOADS_INTERNAL_PRESSURE,
    LOADS_INTERNAL_TEMPERATURE,
    MATERIALS,
    PROP_CEMENT,
    PROP_FORMANTION,
    PROP_MAT_POSITION,
)
from confiacim_api.files_and_folders_handlers import extract_materials_infos
from confiacim_api.logger import logger


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


def generate_loads_template(loads_str: str, loads_infos: dict[str, bool]) -> str:
    """
    Gera o template jinja do conteudo loads.dat. O template gerado é da versão unitaria
    do `FORM `.

    Parameters:
        loads_str: Conteudo do arquivo de `loads.dat` no formato de `str`
        loads_infos: Propriedades que serão dinamicas no template

    Returns:
        Retorna o template jinja
    """
    lines = iter(loads_str.split("\n"))

    new_lines = []
    for line in lines:

        if loads_infos.get(LOADS_EXTERNAL_TEMPERATURE) and "nodalsources" in line:
            new_lines.append(line)
            node, value = next(lines).split()
            new_lines.append(f'{node} {{{{ "%.16e"|format({LOADS_EXTERNAL_TEMPERATURE} * {value}) }}}}')
            new_lines.append(next(lines))

        elif "loads" in line and "nodalloads" not in line and "nodalthermloads" not in line:
            new_lines.append(line)

            load_line = next(lines)
            new_lines.append(load_line)

            npoints = int(load_line.split()[-1])
            if loads_infos.get(LOADS_INTERNAL_PRESSURE):
                for _ in range(npoints):
                    words = next(lines).split()
                    new_lines.append(f'{words[0]} {{{{ "%.16e"|format({LOADS_INTERNAL_PRESSURE} * {words[1]}) }}}}')

            else:
                for _ in range(npoints):
                    new_lines.append(next(lines))

            load_line = next(lines)
            new_lines.append(load_line)

            npoints = int(load_line.split()[-1])
            if loads_infos.get(LOADS_INTERNAL_TEMPERATURE):
                for _ in range(npoints):
                    words = next(lines).split()
                    new_lines.append(
                        f"{words[0]} {words[1]} " f'{{{{ "%.16e"|format({LOADS_INTERNAL_TEMPERATURE} * {words[2]}) }}}}'
                    )
            else:
                for _ in range(npoints):
                    new_lines.append(next(lines))

            new_lines.append(next(lines))
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def generate_hidrationprop_template(hidrationprop_str: str, variables: dict) -> str:
    """
    Gera o template jinja do conteudo `hidrationprop.dat`. O template gerado é da versão
    unitaria do `FORM `.

    Parameters:
        hidrationprop_str: Conteudo do arquivo de `hidrationprop.dat` no formato de `str`
        variables: Propriedades que serão dinamicas no template

    Returns:
        Retorna o template jinja
    """
    lines = iter(hidrationprop_str.split("\n"))

    new_lines = [next(lines)]
    for line in lines:
        new_lines.append(line)

        if "end hidrprop" in line:
            break

        _, prop, npoints = map(int, line.split())

        if prop == HIDRATIONPROP_E_C and variables.get(HIDRATIONPROP_MAP[prop]):
            prop_name = HIDRATIONPROP_MAP[prop]
            for _ in range(npoints):
                words = next(lines).split()
                new_lines.append(f'{float(words[0])} {{{{ "%.16e"|format({prop_name} * {words[1]}) }}}}')

        elif prop == HIDRATIONPROP_POISSON_C and variables.get(HIDRATIONPROP_MAP[prop]):
            prop_name = HIDRATIONPROP_MAP[prop]
            for _ in range(npoints):
                words = next(lines).split()
                new_lines.append(f'{float(words[0])} {{{{ "%.16e"|format({prop_name} * {words[1]}) }}}}')

        elif prop == HIDRATIONPROP_COHESION_C and variables.get(HIDRATIONPROP_MAP[prop]):
            prop_name = HIDRATIONPROP_MAP[prop]
            for _ in range(npoints):
                words = next(lines).split()
                new_lines.append(f'{float(words[0])} {{{{ "%.16e"|format({prop_name} * {words[1]}) }}}}')

        else:
            for _ in range(npoints):
                new_lines.append(next(lines))

    new_lines.append("return\n")
    return "\n".join(new_lines)


def generate_templates(task_id: UUID | None, base_folder: Path, config: dict):
    """
    Gera os templates jinja.

    Parameters:
        task_id: ID da task do celery
        base_folder: Caminho do diretorio base
        config: Configuração do FORM

    """

    def at_least_one_key_in_the_list(key, values):
        return bool(set(key) & set(values))

    materials = base_folder / "materials.dat"
    loads = base_folder / "loads.dat"
    hidrationprop = base_folder / "hidrationprop.dat"

    base_folder_template = base_folder / "templates"
    base_folder_template.mkdir(exist_ok=True)

    variables_name = tuple(var["name"] for var in config["variables"])

    if at_least_one_key_in_the_list(variables_name, MATERIALS):
        logger.info(f"Task {task_id} - Generating materials.jinja ...")

        materilas_str = materials.read_text()
        mat_infos = extract_materials_infos(materilas_str)
        mat_props = {name: getattr(mat_infos, name) for name in variables_name if hasattr(mat_infos, name)}
        jinja_str = generate_materials_template(
            materilas_str,
            mat_props,
        )
        materials_jinja = base_folder_template / "materials.jinja"
        materials_jinja.write_text(jinja_str)

    if at_least_one_key_in_the_list(variables_name, HIDRATIONPROP) and hidrationprop.exists():
        logger.info(f"Task {task_id} - Generating hidrationprop.jinja ...")

        variables = {name: True for name in variables_name}
        hidrationprop_str = hidrationprop.read_text()
        jinja_str = generate_hidrationprop_template(
            hidrationprop_str,
            variables,
        )
        hidrationprop_jinja = base_folder_template / "hidrationprop.jinja"
        hidrationprop_jinja.write_text(jinja_str)

    if at_least_one_key_in_the_list(variables_name, LOADS):
        logger.info(f"Task {task_id} - Generating loads.jinja ...")

        loads_infos = {name: True for name in variables_name}

        loads_str = loads.read_text()
        jinja_str = generate_loads_template(loads_str, loads_infos)

        loads_jinja = base_folder_template / "loads.jinja"
        loads_jinja.write_text(jinja_str)

    logger.info(f"Task {task_id} - Generated.")
