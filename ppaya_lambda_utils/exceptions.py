
class InvokeLambdaFunctionException(Exception):
    """ Raised when the invocation of a lamda function fails """


class WorkflowException(Exception):
    """ Raised when a workflow / state machine fails """
    def __init__(self, msg: str, error_type: str) -> None:
        self.msg = msg
        self.error_type = error_type

    def __str__(self):
        return f'{self.error_type}: {self.msg}'
