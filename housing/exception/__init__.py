import sys


class CustomException(Exception):
    def __init__(self, error_message: Exception, error_details: sys):
        super().__init__(error_message)
        self.error_message = CustomException.error_message_info(error_message, error_details)

    @staticmethod
    def error_message_info(error_message: Exception, error_details: sys) -> str:
        """
        :param error_message: Exception object
        :param error_details: object of sys module to determine the error line number
        :return: string info of error
        """
        # exc_info() -- return thread-safe information about the current exception
        type, value, traceback = error_details.exc_info()
        exception_block_line_number = traceback.tb_frame.f_lineno
        try_block_line_number = traceback.tb_lineno
        file_name = traceback.tb_frame.f_code.co_filename
        error_message = f"""
        Error occurred in file: [{file_name}] at try block line number:  [{try_block_line_number}] 
        and exception block line number : [{exception_block_line_number}]
        error message : [{error_message}]"""
        return error_message

    def __str__(self):
        return self.error_message

    def __repr__(self) -> str:
        return CustomException.__name__.str()
