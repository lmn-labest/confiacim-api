import zipfile
from typing import BinaryIO


def file_case_is_zipfile(case_file: BinaryIO) -> bool:
    is_zip = zipfile.is_zipfile(case_file)
    case_file.seek(0)
    return is_zip
