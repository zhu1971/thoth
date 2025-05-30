from enum import Enum
from typing import List, Optional, Union


class OperandType(Enum):
    VARIABLE = 0
    INTEGER = 1


class Operator(Enum):
    ADDITION = 0
    MULTIPLICATION = 1


class VariableValueType(Enum):
    ADDRESS = 0
    ABSOLUTE = 1
    FUNCTION_CALL = 2


class FunctionCall:
    """
    Function call class
    """

    def __init__(
        self, function, return_value_position: int, arguments: List[str], call_number: int
    ) -> None:
        self.function = function
        self.return_value_position = return_value_position
        self.return_value = self.function.arguments_list(explicit=False, implicit=False, ret=True)[
            return_value_position
        ]
        self.arguments = arguments
        self.call_number = call_number


class Operand:
    """
    Element of an operation, either a variable/list of variables or an integer
    """

    def __init__(self, type: OperandType, value: Union[str, int, List[str], FunctionCall]) -> None:
        self.type = type
        self.value = value

    @property
    def phi_function(self) -> bool:
        """
        Check if a variable operand has several possible values
        """
        if self.type == OperandType.VARIABLE and type(self.value) is list:
            return True
        return False


class VariableValue:
    """
    Value assigned to an SSA variable
    """

    def __init__(self, type: VariableValueType, operation: List) -> None:
        self.type = type
        self.operation = operation


class Variable:
    """
    Variable class
    """

    counter = 0

    def __init__(
        self,
        variable_name: Optional[str] = None,
        function=None,
        basic_block_id: int = None,
        function_result: bool = False,
        is_function_argument: bool = True,
        is_function_return_value: bool = False,
    ) -> None:
        """
        Initialize a new variable
        Args:
            variable_name (Optional String): the name of the variable
        """
        self.variable_name = variable_name
        self.value = None
        self.is_set = False
        self.instance = Variable.counter
        self.name = self.get_name()
        # Local or global variable
        self.local = True
        # Function where the variable is defined
        self.function = function
        # ID of the basic block where the variable is defined
        self.basic_block_id = basic_block_id
        # If the variable is the result of a function
        self.function_result = function_result
        # If the variable is a function argument
        self.is_function_argument = is_function_argument
        # If the variable is a potential return value
        self.is_function_return_value = is_function_return_value
        Variable.counter += 1

    def get_name(self) -> str:
        """
        Return the variable name
        Either a custom name (function arguments/return value) or v<n> by default
        Returns:
            name (String): name of the variable
        """
        # If the variable has a name
        if self.variable_name is not None:
            return "v%s_%s" % (self.instance, self.variable_name)

        # Use default name (v_<n>)
        name = "v%s" % self.instance
        return name
