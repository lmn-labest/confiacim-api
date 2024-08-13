import csv
from io import StringIO

from confiacim_api.models import TencimResult


def write_rc_result_to_csv(results: TencimResult) -> StringIO:
    """Transforma os results para CSV.

    Params:
        results: Resultados de RC do tencim.

    Returns:
       csv: CSV do resultado.

    Info
        Os CSV esta todo em memória essas abordagem pode ser ruim
        caso existam muito passos de tempo na resposta
    """
    csv_file_in_memory = StringIO()

    headers = ["istep", "t", "rc_rankine", "mohr_coulomb_rc"]
    writer = csv.DictWriter(csv_file_in_memory, fieldnames=headers)
    writer.writeheader()

    istep = results.istep if results.istep else ()
    ts = results.t if results.t else ()
    rankine_rc = results.rankine_rc if results.rankine_rc else ()
    mohr_coulomb_rc = results.mohr_coulomb_rc if results.mohr_coulomb_rc else ()

    for i, t, rankine, mohr_coulomb in zip(istep, ts, rankine_rc, mohr_coulomb_rc):
        writer.writerow(
            {
                "istep": i,
                "t": t,
                "rc_rankine": rankine,
                "mohr_coulomb_rc": mohr_coulomb,
            }
        )
    csv_file_in_memory.seek(0)
    return csv_file_in_memory
