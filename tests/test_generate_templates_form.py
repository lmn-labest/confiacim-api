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

MATERIALS_JINJA = """\
materials
1 1 1.999e+11 0.3000 1.400e-05 0 0 4.292e+01 3.894e+06 0 0 0
2 2 1.019e+10 0.3200 0 0 0 3.360e+00
3 1 {{ "%.16e"|format(E_c * 5.0) }} {{ "%.16e"|format(poisson_c * 0.2) }} 9.810e-06 0 7 3.360e+00 2.077e+06 0 1 0 3.200e+06 1.500e+01 2.540e+07 0 0 0 0 0 0 3 8 3.000e-03
4 1 {{ "%.16e"|format(E_f * 2.0) }} {{ "%.16e"|format(poisson_f * 0.1) }} 1.000e-05 0 0 6.006e+00 1.901e+06 0 0 0
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
2 2 1.019e+10 0.3200 0 0 0 3.360e+00\n3 1 {{ "%.16e"|format(E_c * 10190000000.0) }} {{ "%.16e"|format(poisson_c * 0.32) }} 9.810e-06 0 7 3.360e+00 2.077e+06 0 1 0 3.200e+06 1.500e+01 2.540e+07 0 0 0 0 0 0 3 8 3.000e-03
4 1 2.040e+10 0.3600 1.000e-05 0 0 6.006e+00 1.901e+06 0 0 0
end materials
return
"""  # noqa: E501


@pytest.mark.unit
@pytest.mark.parametrize(
    "mat_props,expected",
    [
        (
            {
                "E_c": 5.0,
                "poisson_c": 0.2,
                "E_f": 2.0,
                "poisson_f": 0.1,
            },
            MATERIALS_JINJA,
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
def test_generate_materials_template(mat_props, expected):
    assert generate_materials_template(MATERIALS_STR, mat_props) == expected


@pytest.mark.integration
def test_generate_templates(tmp_path, form_case_config):

    shutil.copy2("tests/fixtures/materials.dat", tmp_path)

    generate_templates(None, tmp_path, form_case_config)

    materials_jinja_str = (tmp_path / "templates/materials.jinja").read_text()

    assert materials_jinja_str == MATERIALS_JINJA_STR
