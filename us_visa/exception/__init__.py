import sys

def write_error_message(error,error_detail:sys):
    _,_,ex_tb = error_detail.exc_info()
    filename= ex_tb.tb_frame.f_code.co_filename
    error_message = "exception occured in filename [ {0} ] line number [ {1} ] error [ {2} ]".format(filename,ex_tb.tb_lineno,error)
    return error_message

class VisaException(Exception):
    def __init__(self,error,error_detail:sys):
        super().__init__(error)
        self.error_message = write_error_message(error,error_detail)

    def __str__(self) -> str:
        return self.error_message