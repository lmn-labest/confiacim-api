import pytest

from confiacim_api.correlations import validation_correlations
from confiacim_api.errors import CorrelationsInvalidError


@pytest.fixture
def variables():
    return [
        {"name": "E_c"},
        {"name": "poisson_c"},
    ]


@pytest.mark.unit
def test_validation_correlations(variables):

    correlations = {
        "E_c, poisson_c": 0.5,
    }

    validation_correlations(variables, correlations)


@pytest.mark.unit
def test_validation_correlations_correlation_needs_to_be_variables(variables):

    correlations = {
        "E_c, poisson_c": 0.5,
        "E_c, intenal_temperature": 0.1,
    }

    msg = "Correlation 'intenal_temperature' is not in the"

    with pytest.raises(CorrelationsInvalidError, match=msg):
        validation_correlations(variables, correlations)


@pytest.mark.unit
@pytest.mark.parametrize(
    "value, msg",
    [
        (1.1, "Correlation 'E_c' is 1.1, it needs to be in range -1.0 and 1.0."),
        (-1.1, "Correlation 'E_c' is -1.1, it needs to be in range -1.0 and 1.0."),
    ],
    ids=["value_gt_1.0", "value_lt_-1.0"],
)
def test_validation_correlations_correlation_needs_to_be_out_range(value, msg, variables):

    correlations = {
        "E_c, poisson_c": value,
    }

    with pytest.raises(CorrelationsInvalidError, match=msg):
        validation_correlations(variables, correlations)
