import pytest

from confiacim_api.models import TencimResult
from confiacim_api.write_csv import write_rc_result_to_csv

CSV_FILE = "istep,t,rc_rankine,mohr_coulomb_rc\r\n1,1.0,100.0,100.0\r\n2,2.0,90.0,80.0\r\n3,3.0,10.0,30.0\r\n"


@pytest.mark.unit
def test_tencim_results_to_csv(tencim_results: TencimResult):

    csv_file = write_rc_result_to_csv(tencim_results)

    assert csv_file.read() == CSV_FILE
