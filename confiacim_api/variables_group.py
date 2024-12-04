from confiacim_api.errors import CorrelationsInvalidError


def validation_correlations(variables: list[dict], correlations: dict[str, float]):
    """
    Verifica se o nome das corelações estão nas variaveis aleatorios. Verifica se o falor é um float.
    Verifica se valor esta entres -1 e 1

    Parameters:
        variables: Variaveis aleatorios do `FORM`
        correlations: correlação de variaveis


    """
    variables_name = {v["name"] for v in variables}

    for k, v in correlations.items():
        var1, var2 = list(map(str.strip, k.split(",")))

        if var1 not in variables_name:
            raise CorrelationsInvalidError(f"Correlation '{var1}' is not in the {variables_name}.")

        if var2 not in variables_name:
            raise CorrelationsInvalidError(f"Correlation '{var2}' is not in the {variables_name}.")

        value = float(v)

        if not -1.0 < value < 1.0:
            raise CorrelationsInvalidError(f"Correlation '{var1}' is {value}, it needs to be in range -1.0 and 1.0.")
