import shutil

import pytest

from confiacim_api.generate_templates_form import (
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
    materials_jinja_str = generate_materials_template(MATERIALS_STR, mat_props)
    assert materials_jinja_str == expected_str


@pytest.mark.integration
def test_generate_templates(tmp_path, form_case_config):

    shutil.copy2("tests/fixtures/materials.dat", tmp_path)

    generate_templates(None, tmp_path, form_case_config)

    materials_jinja_str = (tmp_path / "templates/materials.jinja").read_text()

    assert materials_jinja_str == MATERIALS_JINJA_STR
