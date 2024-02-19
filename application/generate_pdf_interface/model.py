from application.reportgen.gen_A002V2 import A002V2
from application.reportgen.gen_E001V1 import E001V1
from application.reportgen.gen_S001v1 import S001V1
from application.reportgen.gen_F001V1 import F001V1
from functools import partial


def generate_pdf_factory(report_code: str) -> object:
    report_code_generate_pdf_version_map = {
        'A002V2': partial(A002V2),
        'E001V1': partial(E001V1),
        'S001V1': partial(S001V1),
        'F001V1': partial(F001V1),
    }
    return report_code_generate_pdf_version_map[report_code]()
fake_choose_generate_pdf_version = generate_pdf_factory
