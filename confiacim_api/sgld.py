from math import factorial, gamma, pow, sqrt


def mom_espec(sigma, r, k):
    soma = 0
    for n in range(31):  # 0 to 30
        soma += (pow(k * sigma, 2 * n) / factorial(2 * n)) * pow(r, (2 * n / r)) * gamma((2 * n + 1) / r)

    return (1 / gamma(1 / r)) * soma


def sgld_params(mean: float, cov: float, sigma: float, r: float) -> tuple[float, float]:
    """Conversão dos parametros da SGLD

    Paramenters:
        mean: media
        cov: coeficiente de variação.
        sigma: sigma da SGLD
        r: sigma da SGLD_

    Returns:
       Theta e beta da SGLD
    """
    m_x = mean
    sigma_x = m_x * cov

    m_y = mom_espec(sigma, r, 1)
    sigma_y = sqrt(mom_espec(sigma, r, 2) - pow(mom_espec(sigma, r, 1), 2))
    theta_1 = sigma_x / sigma_y
    beta_1 = m_x - theta_1 * m_y

    return theta_1, beta_1
