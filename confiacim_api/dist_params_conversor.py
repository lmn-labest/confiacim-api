from confiacim_api.errors import InvalidDistNameError
from confiacim_api.sgld import sgld_params


def dist_params(variable: dict) -> dict:
    """Converte os parametros da distruições da plataforma web par o confiacim core

    Parameters:
        variable: variavel do confiacim web

    Raises:
        InvalidDistNameError: Nome invalido da distruibuição.

    Returns:
        variável para confiacim core
    """
    var_name = variable["name"]
    dist = variable["dist"]
    dist_name = dist["name"]

    if dist_name in ("normal", "lognormal", "gumbel_r", "weibull_min"):
        new_dist = {
            "name": dist_name,
            "params": {
                "mean": dist["params"]["param1"],
                "cov": dist["params"]["param2"],
            },
        }

    elif "sgld_t" == dist_name:

        mean, cov, sigma, r = (
            dist["params"]["param1"],
            dist["params"]["param2"],
            dist["params"]["param3"],
            dist["params"]["param4"],
        )

        theta, b = sgld_params(mean, cov, sigma, r)
        new_dist = {
            "name": "sgld_lower_t",
            "params": {
                "theta": theta,
                "b": b,
                "sigma": sigma,
                "r": r,
                "x_lower_limit": 0.0,
            },
        }

        if var_name == "poisson_c" or var_name == "poisson_f":
            new_dist = {
                "name": "sgld_lower_upper_t",
                "params": {
                    "theta": theta,
                    "b": b,
                    "sigma": sigma,
                    "r": r,
                    "x_lower_limit": 0.0,
                    "x_upper_limit": 0.49,
                    "scale_factor": mean,
                },
            }
    else:
        raise InvalidDistNameError(f"'{dist_name}' is invalid dist name.")

    return {
        "name": var_name,
        "dist": new_dist,
    }


def convert_variable_web_to_core(variables: list[dict]) -> list[dict]:
    """
    Converte a lista das distruições da plataforma web para um lista de variaveis
    do confiacim core

    Parameters:
        variables: lista de variavies do confiacim web

    Returns:
        Variáveies para confiacim core
    """
    return [dist_params(v) for v in variables]
