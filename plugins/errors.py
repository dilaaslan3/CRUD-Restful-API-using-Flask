class DilaError(Exception):
    def __init__(self, err_msg, err_code, status_code):
        self.err_msg = err_msg
        self.err_code = err_code
        self.status_code = status_code
