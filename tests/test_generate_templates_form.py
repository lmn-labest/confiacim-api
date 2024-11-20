import shutil

import pytest

from confiacim_api.generate_templates_form import (
    generate_hidrationprop_template,
    generate_loads_template,
    generate_materials_template,
    generate_templates,
)

MATERIALS_STR = """\
materials
    1 1 1.999e+11 0.3000 1.400e-05 0 0 4.292e+01 3.894e+06 0 0 0
    2 2 1.019e+10 0.3200 0 0 0 3.360e+00
    3 1 1.019e+10 0.3200 9.810e-06 0 7 3.360e+00 2.077e+06 0 1 0 3.200e+06 1.500e+01 2.540e+07 0 0 0 0 0 0 3 8 3.000e-03
    4 1 2.040e+10 0.3600 1.000e-05 0 0 6.006e+00 1.901e+06 0 0 0
end materials
return
"""

MATERIALS_JINJA_ALL = """\
materials
1 1 1.999e+11 0.3000 1.400e-05 0 0 4.292e+01 3.894e+06 0 0 0
2 2 1.019e+10 0.3200 0 0 0 3.360e+00
3 1 {{ "%.16e"|format(E_c * 5.0) }} {{ "%.16e"|format(poisson_c * 0.2) }} {{ "%.16e"|format(thermal_expansion_c * 2.0) }} 0 7 {{ "%.16e"|format(thermal_conductivity_c * 10.0) }} {{ "%.16e"|format(volumetric_heat_capacity_c * 0.1) }} 0 1 0 3.200e+06 {{ "%.16e"|format(friction_angle_c * 0.3) }} {{ "%.16e"|format(cohesion_c * 0.4) }} 0 0 0 0 0 0 3 8 3.000e-03
4 1 {{ "%.16e"|format(E_f * 2.0) }} {{ "%.16e"|format(poisson_f * 0.1) }} {{ "%.16e"|format(thermal_expansion_f * 0.4) }} 0 0 {{ "%.16e"|format(thermal_conductivity_f * 20.0) }} {{ "%.16e"|format(volumetric_heat_capacity_f * 0.3) }} 0 0 0
end materials
return
"""  # noqa: E501

MATERIALS_JINJA_E_C_POISSON_F = """\
materials
1 1 1.999e+11 0.3000 1.400e-05 0 0 4.292e+01 3.894e+06 0 0 0
2 2 1.019e+10 0.3200 0 0 0 3.360e+00
3 1 {{ "%.16e"|format(E_c * 5.0) }} 0.3200 9.810e-06 0 7 3.360e+00 2.077e+06 0 1 0 3.200e+06 1.500e+01 2.540e+07 0 0 0 0 0 0 3 8 3.000e-03
4 1 2.040e+10 {{ "%.16e"|format(poisson_f * 0.1) }} 1.000e-05 0 0 6.006e+00 1.901e+06 0 0 0
end materials
return
"""  # noqa: E501

MATERIALS_JINJA_STR = """\
materials
1 1 1.999e+11 0.3000 1.400e-05 0 0 4.292e+01 3.894e+06 0 0 0
2 2 1.019e+10 0.3200 0 0 0 3.360e+00
3 1 {{ "%.16e"|format(E_c * 10190000000.0) }} {{ "%.16e"|format(poisson_c * 0.32) }} 9.810e-06 0 7 3.360e+00 2.077e+06 0 1 0 3.200e+06 1.500e+01 2.540e+07 0 0 0 0 0 0 3 8 3.000e-03
4 1 2.040e+10 0.3600 1.000e-05 0 0 6.006e+00 1.901e+06 0 0 0
end materials
return
"""  # noqa: E501

LOAD_JINJA_STR = """\
constraindisp
83 1
end constraindisp
constraintemp
83 1
end constraintemp
nodalloads
1 1
end nodalloads
nodalthermloads
1 2
end nodalthermloads
nodalsources
83 291.639
end nodalsources
loads
1 11 0.11123 4
0    0.0000e+00
600  0.0000e+00
1200 6.8947e+07
1800 6.8947e+07
2 4 3
600  0 299.073
1200 0 299.073
1800 0 299.073
end loads
return
"""  # noqa: E501

LOAD_JINJA_ALL = """\
constraindisp
83 1
end constraindisp
constraintemp
83 1
end constraintemp
nodalloads
1 1
end nodalloads
nodalthermloads
1 2
end nodalthermloads
nodalsources
83 {{ "%.16e"|format(external_temperature * 291.639) }}
end nodalsources
loads
1 11 0.11123 4
0 {{ "%.16e"|format(internal_pressure * 0.0000e+00) }}
600 {{ "%.16e"|format(internal_pressure * 0.0000e+00) }}
1200 {{ "%.16e"|format(internal_pressure * 6.8947e+07) }}
1800 {{ "%.16e"|format(internal_pressure * 6.8947e+07) }}
2 4 3
600 0 {{ "%.16e"|format(internal_temperature * 299.073) }}
1200 0 {{ "%.16e"|format(internal_temperature * 299.073) }}
1800 0 {{ "%.16e"|format(internal_temperature * 299.073) }}
end loads
return
"""  # noqa: E501

LOAD_JINJA_INTERNAL_TEMPERATURE = """\
constraindisp
83 1
end constraindisp
constraintemp
83 1
end constraintemp
nodalloads
1 1
end nodalloads
nodalthermloads
1 2
end nodalthermloads
nodalsources
83 291.639
end nodalsources
loads
1 11 0.11123 4
0    0.0000e+00
600  0.0000e+00
1200 6.8947e+07
1800 6.8947e+07
2 4 3
600 0 {{ "%.16e"|format(internal_temperature * 299.073) }}
1200 0 {{ "%.16e"|format(internal_temperature * 299.073) }}
1800 0 {{ "%.16e"|format(internal_temperature * 299.073) }}
end loads
return
"""  # noqa: E501

LOADS_JINJA_STR = """\
constraindisp
83 1
end constraindisp
constraintemp
83 1
end constraintemp
nodalloads
1 1
end nodalloads
nodalthermloads
1 2
end nodalthermloads
nodalsources
83 291.639
end nodalsources
loads
1 11 0.11123 4
0 {{ "%.16e"|format(internal_pressure * 0.0000e+00) }}
600 {{ "%.16e"|format(internal_pressure * 0.0000e+00) }}
1200 {{ "%.16e"|format(internal_pressure * 6.8947e+07) }}
1800 {{ "%.16e"|format(internal_pressure * 6.8947e+07) }}
2 4 3
600 0 {{ "%.16e"|format(internal_temperature * 299.073) }}
1200 0 {{ "%.16e"|format(internal_temperature * 299.073) }}
1800 0 {{ "%.16e"|format(internal_temperature * 299.073) }}
end loads
return
"""  # noqa: E501

HIDRATION_STR = """\
hidrprop
3 1 7
0.00 2.200e+08
0.04 2.200e+08
0.045 8.592e+08
0.08 2.429e+09
0.20 4.858e+09
0.49 8.148e+09
1.00 1.190e+10
3 2 4
0.00 4.900e-01
0.04 4.900e-01
0.08 1.800e-01
1.00 1.800e-01
3 7 3
0.00 2.420e+06
0.50 1.936e+06
1.00 1.936e+06
3 11 3
0.00 8.000e+04
0.04 8.000e+04
1.00 4.708e+06
3 13 3
0.00 8.000e+05
0.04 8.000e+05
1.00 1.970e+07
end hidrprop
return
"""  # noqa: E501


HIDRATION_JINJA_ALL = """\
hidrprop
3 1 7
0.0 {{ "%.16e"|format(E_c * 2.200e+08) }}
0.04 {{ "%.16e"|format(E_c * 2.200e+08) }}
0.045 {{ "%.16e"|format(E_c * 8.592e+08) }}
0.08 {{ "%.16e"|format(E_c * 2.429e+09) }}
0.2 {{ "%.16e"|format(E_c * 4.858e+09) }}
0.49 {{ "%.16e"|format(E_c * 8.148e+09) }}
1.0 {{ "%.16e"|format(E_c * 1.190e+10) }}
3 2 4
0.0 {{ "%.16e"|format(poisson_c * 4.900e-01) }}
0.04 {{ "%.16e"|format(poisson_c * 4.900e-01) }}
0.08 {{ "%.16e"|format(poisson_c * 1.800e-01) }}
1.0 {{ "%.16e"|format(poisson_c * 1.800e-01) }}
3 7 3
0.00 2.420e+06
0.50 1.936e+06
1.00 1.936e+06
3 11 3
0.00 8.000e+04
0.04 8.000e+04
1.00 4.708e+06
3 13 3
0.0 {{ "%.16e"|format(cohesion_c * 8.000e+05) }}
0.04 {{ "%.16e"|format(cohesion_c * 8.000e+05) }}
1.0 {{ "%.16e"|format(cohesion_c * 1.970e+07) }}
end hidrprop
return
"""  # noqa: E501

HIDRATION_JINJA_E_C = """\
hidrprop
3 1 7
0.0 {{ "%.16e"|format(E_c * 2.200e+08) }}
0.04 {{ "%.16e"|format(E_c * 2.200e+08) }}
0.045 {{ "%.16e"|format(E_c * 8.592e+08) }}
0.08 {{ "%.16e"|format(E_c * 2.429e+09) }}
0.2 {{ "%.16e"|format(E_c * 4.858e+09) }}
0.49 {{ "%.16e"|format(E_c * 8.148e+09) }}
1.0 {{ "%.16e"|format(E_c * 1.190e+10) }}
3 2 4
0.00 4.900e-01
0.04 4.900e-01
0.08 1.800e-01
1.00 1.800e-01
3 7 3
0.00 2.420e+06
0.50 1.936e+06
1.00 1.936e+06
3 11 3
0.00 8.000e+04
0.04 8.000e+04
1.00 4.708e+06
3 13 3
0.00 8.000e+05
0.04 8.000e+05
1.00 1.970e+07
end hidrprop
return
"""  # noqa: E501

HIDRATION_JINJA_STR = """\
hidrprop
3 1 7
0.0 {{ "%.16e"|format(E_c * 2.200e+08) }}
0.04 {{ "%.16e"|format(E_c * 2.200e+08) }}
0.045 {{ "%.16e"|format(E_c * 8.592e+08) }}
0.08 {{ "%.16e"|format(E_c * 2.429e+09) }}
0.2 {{ "%.16e"|format(E_c * 4.858e+09) }}
0.49 {{ "%.16e"|format(E_c * 8.148e+09) }}
1.0 {{ "%.16e"|format(E_c * 1.190e+10) }}
3 2 4
0.0 {{ "%.16e"|format(poisson_c * 4.900e-01) }}
0.04 {{ "%.16e"|format(poisson_c * 4.900e-01) }}
0.08 {{ "%.16e"|format(poisson_c * 1.800e-01) }}
1.0 {{ "%.16e"|format(poisson_c * 1.800e-01) }}
3 7 3
0.00 2.420e+06
0.50 1.936e+06
1.00 1.936e+06
3 11 3
0.00 8.000e+04
0.04 8.000e+04
1.00 4.708e+06
3 13 3
0.00 8.000e+05
0.04 8.000e+05
1.00 1.970e+07
end hidrprop
return
"""  # noqa: E501


@pytest.mark.unit
@pytest.mark.parametrize(
    "mat_props,expected_str",
    [
        (
            {
                # Cement
                "E_c": 5.0,
                "poisson_c": 0.2,
                "thermal_expansion_c": 2.0,
                "thermal_conductivity_c": 10.0,
                "volumetric_heat_capacity_c": 0.1,
                "friction_angle_c": 0.3,
                "cohesion_c": 0.4,
                # Formantion
                "E_f": 2.0,
                "poisson_f": 0.1,
                "thermal_expansion_f": 0.4,
                "thermal_conductivity_f": 20.0,
                "volumetric_heat_capacity_f": 0.3,
            },
            MATERIALS_JINJA_ALL,
        ),
        (
            {
                "E_c": 5.0,
                "poisson_f": 0.1,
            },
            MATERIALS_JINJA_E_C_POISSON_F,
        ),
    ],
    ids=[
        "all",
        "E_c_poisson_f",
    ],
)
def test_generate_materials_template(mat_props, expected_str):
    jinja_str = generate_materials_template(MATERIALS_STR, mat_props)
    assert jinja_str == expected_str


@pytest.mark.unit
@pytest.mark.parametrize(
    "loads_infos,expected_str",
    [
        (
            {
                "external_temperature": True,
                "internal_temperature": True,
                "internal_pressure": True,
            },
            LOAD_JINJA_ALL,
        ),
        (
            {
                "internal_temperature": True,
            },
            LOAD_JINJA_INTERNAL_TEMPERATURE,
        ),
    ],
    ids=[
        "all",
        "internal_temperature",
    ],
)
def test_generate_loads_template(loads_infos, expected_str):
    jinja_str = generate_loads_template(LOAD_JINJA_STR, loads_infos)
    assert jinja_str == expected_str


@pytest.mark.unit
@pytest.mark.parametrize(
    "mat_props,expected_str",
    [
        (
            {
                "E_c": True,
                "poisson_c": True,
                "cohesion_c": True,
            },
            HIDRATION_JINJA_ALL,
        ),
        (
            {
                "E_c": True,
            },
            HIDRATION_JINJA_E_C,
        ),
    ],
    ids=[
        "all",
        "E_c",
    ],
)
def test_generate_hidration_template(mat_props, expected_str):
    jinja_str = generate_hidrationprop_template(HIDRATION_STR, mat_props)
    assert jinja_str == expected_str


@pytest.mark.integration
def test_generate_templates(tmp_path, form_case_config):

    shutil.copy2("tests/fixtures/materials.dat", tmp_path)
    shutil.copy2("tests/fixtures/hidrationprop.dat", tmp_path)
    shutil.copy2("tests/fixtures/loads.dat", tmp_path)

    generate_templates(None, tmp_path, form_case_config)

    materials_jinja_str = (tmp_path / "templates/materials.jinja").read_text()
    hidrprop_jinja_str = (tmp_path / "templates/hidrationprop.jinja").read_text()
    loads_jinja_str = (tmp_path / "templates/loads.jinja").read_text()

    assert materials_jinja_str == MATERIALS_JINJA_STR
    assert hidrprop_jinja_str == HIDRATION_JINJA_STR
    assert loads_jinja_str == LOADS_JINJA_STR


@pytest.mark.integration
def test_generate_templates_must_generate_hidration_only_with_file_exists(tmp_path, form_case_config):

    shutil.copy2("tests/fixtures/materials.dat", tmp_path)
    shutil.copy2("tests/fixtures/loads.dat", tmp_path)

    generate_templates(None, tmp_path, form_case_config)

    assert (tmp_path / "templates/materials.jinja").exists()
    assert not (tmp_path / "templates/hidrationprop.jinja").exists()
    assert (tmp_path / "templates/loads.jinja").exists()


@pytest.mark.integration
def test_generate_templates_for_this_vars_must_generate_only_loads(tmp_path):

    shutil.copy2("tests/fixtures/materials.dat", tmp_path)
    shutil.copy2("tests/fixtures/loads.dat", tmp_path)
    shutil.copy2("tests/fixtures/hidrationprop.dat", tmp_path)

    config = {
        "variables": [
            {
                "name": "internal_pressure",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": 1.0,
                        "cov": 0.1,
                    },
                },
            },
        ]
    }
    generate_templates(None, tmp_path, config)

    assert not (tmp_path / "templates/materials.jinja").exists()
    assert not (tmp_path / "templates/hidrationprop.jinja").exists()
    assert (tmp_path / "templates/loads.jinja").exists()


@pytest.mark.integration
def test_generate_templates_for_this_vars_must_generate_only_materials(tmp_path):

    shutil.copy2("tests/fixtures/materials.dat", tmp_path)
    shutil.copy2("tests/fixtures/loads.dat", tmp_path)
    shutil.copy2("tests/fixtures/hidrationprop.dat", tmp_path)

    config = {
        "variables": [
            {
                "name": "volumetric_heat_capacity_f",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": 1.0,
                        "cov": 0.1,
                    },
                },
            },
        ]
    }
    generate_templates(None, tmp_path, config)

    assert (tmp_path / "templates/materials.jinja").exists()
    assert not (tmp_path / "templates/hidrationprop.jinja").exists()
    assert not (tmp_path / "templates/loads.jinja").exists()


@pytest.mark.integration
def test_generate_templates_for_this_vars_must_generate_materials_and_hidration(tmp_path):

    shutil.copy2("tests/fixtures/materials.dat", tmp_path)
    shutil.copy2("tests/fixtures/loads.dat", tmp_path)
    shutil.copy2("tests/fixtures/hidrationprop.dat", tmp_path)

    config = {
        "variables": [
            {
                "name": "cohesion_c",
                "dist": {
                    "name": "lognormal",
                    "params": {
                        "mean": 1.0,
                        "cov": 0.1,
                    },
                },
            },
        ]
    }

    generate_templates(None, tmp_path, config)

    assert (tmp_path / "templates/materials.jinja").exists()
    assert (tmp_path / "templates/hidrationprop.jinja").exists()
    assert not (tmp_path / "templates/loads.jinja").exists()
