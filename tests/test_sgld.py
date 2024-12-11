import pytest

from confiacim_api.sgld import mom_espec, sgld_params


@pytest.mark.unit
@pytest.mark.parametrize(
    "theta, beta, mean, cov, sigma, r",
    [
        (
            9.317964232649038,
            -8.31853610727778,
            1.0,
            0.103257968221752,
            0.0069132641498648,
            0.842595342406661,
        ),
        (
            9.18294284107865,
            -8.183520222333458,
            1.0,
            0.103,
            0.007,
            0.843,
        ),
        (
            6.046344214293859,
            -5.048251952885891,
            1.0,
            0.152,
            0.019,
            1.111,
        ),
        (
            2.1811613606594547,
            -1.187565405662586,
            1.0,
            0.168,
            0.066,
            1.410,
        ),
        (
            0.6046135006303845,
            0.3940191650513911,
            1.0,
            0.041,
            0.042,
            0.845,
        ),
        (
            0.06236260470559975,
            0.9375656096440308,
            1.0,
            0.003,
            0.037,
            1.148,
        ),
    ],
    ids=[
        "E",
        "E_c",
        "poisson_c",
        "thermal_expansion_c",
        "thermal_conductivity_c",
        "volumetric_heat_capacity_c",
    ],
)
def test_sgld_params(theta, beta, mean, cov, sigma, r):

    theta_1, beta_1 = sgld_params(mean, cov, sigma, r)

    assert theta_1 == pytest.approx(theta)
    assert beta_1 == pytest.approx(beta)


@pytest.mark.unit
@pytest.mark.parametrize(
    "sigma, r, k, result",
    [
        (1, 1, 1, 30.999999999),
        (2, 2, 2, 2980.9579854),
    ],
    ids=["A", "B"],
)
def test_mom_espec(sigma, r, k, result):
    assert mom_espec(sigma, r, k) == pytest.approx(result)
