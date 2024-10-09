import pytest
from pydantic_core import ValidationError

from confiacim_api.schemes import FormVariables, RandomDistribution


@pytest.mark.unit
@pytest.mark.parametrize(
    "name",
    [
        "E_c",
        "poisson_c",
        "E_f",
        "poisson_f",
    ],
)
def test_valid_form_variables(name):

    variable = FormVariables(
        name=name,
        dist=RandomDistribution(
            name="normal",
            params={
                "mean": 1.0,
                "cov": 0.1,
            },
        ),
    )

    assert variable.name == name


@pytest.mark.unit
def test_invalid_choice_form_variables_name():

    msg = "Input should be 'E_c', 'poisson_c', 'E_f' or 'poisson_f'"
    with pytest.raises(ValidationError, match=msg):
        FormVariables(
            name="invalid_name",
            dist=RandomDistribution(
                name="normal",
                params={
                    "mean": 1.0,
                    "cov": 0.1,
                },
            ),
        )


@pytest.mark.unit
@pytest.mark.parametrize(
    "name",
    [
        "normal",
        "lognormal",
        "gumbel_r",
        "weibull_min",
        "triang",
        "sgld",
        "sgld_t",
    ],
)
def test_valid_distribution_name(name):

    variable = FormVariables(
        name="E_c",
        dist=RandomDistribution(
            name=name,
            params={
                "mean": 1.0,
                "cov": 0.1,
            },
        ),
    )

    assert variable.dist.name == name


@pytest.mark.unit
def test_invalid_choice_distribution_name():

    msg = "Input should be 'normal', 'lognormal', 'gumbel_r', 'weibull_min', 'triang', 'sgld' or 'sgld_t'"
    with pytest.raises(ValidationError, match=msg):
        FormVariables(
            name="E_c",
            dist=RandomDistribution(
                name="invalid_name",
                params={
                    "mean": 1.0,
                    "cov": 0.1,
                },
            ),
        )
