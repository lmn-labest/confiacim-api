import pytest

from confiacim_api.dist_params_conversor import convert_variable_web_to_core, dist_params
from confiacim_api.errors import InvalidDistNameError


@pytest.mark.unit
@pytest.mark.parametrize(
    "var_web, dist_form",
    [
        (
            {
                "name": "E_c",
                "dist": {
                    "name": "normal",
                    "params": {"param1": 1.0, "param2": 0.1},
                },
            },
            {
                "name": "normal",
                "params": {"mean": 1.0, "cov": 0.1},
            },
        ),
        (
            {
                "name": "E_c",
                "dist": {
                    "name": "lognormal",
                    "params": {"param1": 1.0, "param2": 0.1},
                },
            },
            {
                "name": "lognormal",
                "params": {"mean": 1.0, "cov": 0.1},
            },
        ),
        (
            {
                "name": "E_c",
                "dist": {
                    "name": "gumbel_r",
                    "params": {"param1": 1.0, "param2": 0.1},
                },
            },
            {
                "name": "gumbel_r",
                "params": {"mean": 1.0, "cov": 0.1},
            },
        ),
        (
            {
                "name": "E_c",
                "dist": {
                    "name": "weibull_min",
                    "params": {"param1": 1.0, "param2": 0.1},
                },
            },
            {
                "name": "weibull_min",
                "params": {"mean": 1.0, "cov": 0.1},
            },
        ),
        (
            {
                "name": "E_c",
                "dist": {
                    "name": "sgld_t",
                    "params": {"param1": 1.0, "param2": 0.103, "param3": 0.007, "param4": 0.843},
                },
            },
            {
                "name": "sgld_lower_t",
                "params": {
                    "theta": 9.182942841086755,
                    "b": -8.183520222341564,
                    "sigma": 0.007,
                    "r": 0.843,
                    "x_lower_limit": 0.0,
                },
            },
        ),
        (
            {
                "name": "poisson_c",
                "dist": {
                    "name": "sgld_t",
                    "params": {"param1": 1.0, "param2": 0.103, "param3": 0.007, "param4": 0.843},
                },
            },
            {
                "name": "sgld_lower_upper_t",
                "params": {
                    "theta": 9.182942841086755,
                    "b": -8.183520222341564,
                    "sigma": 0.007,
                    "r": 0.843,
                    "x_lower_limit": 0.0,
                    "x_upper_limit": 0.49,
                    "scale_factor": 1.0,
                },
            },
        ),
    ],
    ids=[
        "normal",
        "lognormal",
        "gumbel_r",
        "weibull_min",
        "sgld_lower_t",
        "sgld_lower_upper_t",
    ],
)
def test_dist_params_conversion(var_web, dist_form):

    results = dist_params(var_web)

    assert results["name"] == var_web["name"]
    assert results["dist"] == dist_form


@pytest.mark.unit
def test_dist_params_conversion_invalid_name():

    var = {
        "name": "poisson_c",
        "dist": {
            "name": "invalid",
            "params": {"param1": 1.0, "param2": 0.103},
        },
    }

    msg = "'invalid' is invalid dist name."

    with pytest.raises(InvalidDistNameError, match=msg):
        dist_params(var)


def test_convert_variable_web_to_core():

    variables = [
        {
            "name": "E_c",
            "dist": {
                "name": "normal",
                "params": {"param1": 1.0, "param2": 0.1},
            },
        },
        {
            "name": "poisson_c",
            "dist": {
                "name": "lognormal",
                "params": {"param1": 1.0, "param2": 0.103},
            },
        },
    ]

    result = convert_variable_web_to_core(variables)

    assert result[0] == {
        "name": "E_c",
        "dist": {
            "name": "normal",
            "params": {"mean": 1.0, "cov": 0.1},
        },
    }

    assert result[1] == {
        "name": "poisson_c",
        "dist": {
            "name": "lognormal",
            "params": {"mean": 1.0, "cov": 0.103},
        },
    }
