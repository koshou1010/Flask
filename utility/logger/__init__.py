from .globals import logger_manager


def initialize(app, echo: bool = False):
    logger_manager.setup(
        filename = './log/report_server_log',
        level='info',
        when='D',
        back_count=0,
        fmt='[%(asctime)s %(levelname)-3s] %(message)s'
    )
    pass