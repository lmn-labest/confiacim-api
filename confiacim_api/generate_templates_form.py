PROP_MAT_POSITION = {
    "E_c": 2,
    "poisson_c": 3,
    "E_f": 2,
    "poisson_f": 3,
}

PROP_CEMENT = "E_c,poisson_c"
PROP_FORMANTION = "E_f,poisson_f"
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
