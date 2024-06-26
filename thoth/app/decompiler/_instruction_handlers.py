import copy
from thoth.app import utils
from thoth.app.decompiler.variable import (
    FunctionCall,
    Operand,
    OperandType,
    Operator,
    VariableValue,
    VariableValueType,
)
from thoth.app.disassembler.instruction import Instruction


def _handle_assert_eq_decomp(self, instruction: Instruction) -> str:
    """Handle the ASSERT_EQ opcode
    Args:
        instruction (Instruction): intruction to decompile
    Returns:
        String: The formated ASSERT_EQ instruction
    """
    source_code = ""
    is_assert = ""
    equal = "="
    assertion = []

    # Generate the phi function representation
    phi_node_variables = []

    # Generate the phi function representation
    if self.current_basic_block.is_phi_node and not self.first_pass:
        phi_node_variables = self.get_phi_node_variables()
        variables_names = [variable.name for variable in self.get_phi_node_variables()]
        # Phi function is represented in the form Φ(var1, var2, ..., var<n>)
        phi_node_representation = "Φ(%s)" % ", ".join(variables_names)
    elif (
        self.block_new_variables == 0
        and len(self.current_function.cfg.parents(self.current_basic_block)) != 0
    ):
        phi_node_variables = self.get_phi_node_variables()
        if len(phi_node_variables) != 0:
            phi_node_representation = phi_node_variables[-1].name

    # Registers and offsets
    destination_register = instruction.dstRegister.lower()
    destination_offset = int(instruction.offDest) if instruction.offDest else 0
    op0_register = instruction.op0Register.lower()
    offset_1 = int(instruction.off1) if instruction.off1 else 0
    op1_register = instruction.op1Addr.lower()
    offset_2 = int(instruction.off2) if instruction.off2 else 0

    OPERATORS = {"ADD": "+", "MUL": "*"}

    destination_offset = int(instruction.offDest) if instruction.offDest else 0

    if "OP1" in instruction.res:
        # <Variable> = <integer>
        if "IMM" in instruction.op1Addr:
            value = utils.value_to_string(int(instruction.imm), (instruction.prime))
            if value == "":
                value = utils.field_element_repr(int(instruction.imm), instruction.prime)

            variable = self.ssa.get_variable(destination_register, destination_offset)
            if variable[2].value is not None or self.assertion:
                is_assert = "assert "
            variable_value = utils.field_element_repr(int(instruction.imm), instruction.prime)

            # Set variable value
            try:
                variable_value_int = int(variable_value)
            except:
                variable_value_int = int(variable_value, base=16)
            if variable[2].value is None and not self.assertion:
                variable[2].value = VariableValue(
                    type=VariableValueType.ABSOLUTE,
                    operation=[Operand(type=OperandType.INTEGER, value=variable_value_int)],
                )

            source_code += self.print_instruction_decomp(
                f"{is_assert}{variable[1]} {equal} {variable_value}",
                color=utils.color.GREEN,
            )
            if is_assert:
                assertion = [variable[1], variable_value]

            # Variable value (hex or string)
            source_code += self.print_instruction_decomp(
                f"// {value}",
                color=utils.color.CYAN,
                tab_count=1,
            )
        # <variable> = [<variable> +/- <integer>]
        elif "OP0" in instruction.op1Addr:
            variable = self.ssa.get_variable(destination_register, destination_offset)
            if variable[2].value is not None or self.assertion:
                is_assert = "assert "
                equal = "=="
            if self.ssa.get_variable(op0_register, offset_1)[2] in phi_node_variables:
                operand = phi_node_representation
                variable_operand_1 = Operand(
                    type=OperandType.VARIABLE,
                    value=[variable.name for variable in self.get_phi_node_variables()],
                )
            else:
                operand = self.ssa.get_variable(op0_register, offset_1)[1]
                variable_operand_1 = Operand(type=OperandType.VARIABLE, value=[operand])

            operator = Operator.ADDITION
            variable_operand_2 = Operand(type=OperandType.INTEGER, value=[0])

            value_off2 = instruction.off2
            sign = ""
            try:
                value_off2 = int(value_off2)
                variable_operand_2 = Operand(type=OperandType.INTEGER, value=[value_off2])
                sign = " + " if value_off2 >= 0 else " - "
            except Exception:
                pass

            # Set variable value
            if variable[2].value is None and not self.assertion:
                variable[2].value = VariableValue(
                    type=VariableValueType.ADDRESS,
                    operation=[variable_operand_1, operator, variable_operand_2],
                )
            source_code += self.print_instruction_decomp(
                f"{is_assert}{variable[1]} {equal} [{operand}{sign}{value_off2}]",
                color=utils.color.GREEN,
            )

        # <variable> = <variable>
        else:
            variable = self.ssa.get_variable(destination_register, destination_offset)
            if variable[2].value is not None or self.assertion:
                is_assert = "assert "
            if self.ssa.get_variable(op1_register, offset_2)[2] in phi_node_variables:
                variable_value = phi_node_representation
                # Set variable value
                if variable[2].value is None and not self.assertion:
                    variable[2].value = VariableValue(
                        type=VariableValueType.ABSOLUTE,
                        operation=[
                            Operand(
                                type=OperandType.VARIABLE,
                                value=[variable.name for variable in phi_node_variables],
                            )
                        ],
                    )
            else:
                variable_value = self.ssa.get_variable(op1_register, offset_2)[1]
                # Set variable value
                if variable[2].value is None and not self.assertion:
                    variable[2].value = VariableValue(
                        type=VariableValueType.ABSOLUTE,
                        operation=[Operand(type=OperandType.VARIABLE, value=[variable_value])],
                    )
            source_code += self.print_instruction_decomp(
                f"{is_assert}{variable[1]} {equal} {variable_value}",
                color=utils.color.GREEN,
            )
    # <variable> = <variable> +/- <variable>
    else:
        op = OPERATORS[instruction.res]
        if "IMM" not in instruction.op1Addr:
            variable = self.ssa.get_variable(destination_register, destination_offset)
            if variable[2].value is not None or self.assertion:
                is_assert = "assert "
            if self.ssa.get_variable(op0_register, offset_1)[2] in phi_node_variables:
                operand_1 = phi_node_representation
                variable_operand_1 = Operand(
                    type=OperandType.VARIABLE,
                    value=[variable.name for variable in phi_node_variables],
                )
            else:
                operand_1 = self.ssa.get_variable(op0_register, offset_1)[1]
                variable_operand_1 = Operand(type=OperandType.VARIABLE, value=[operand_1])
            if self.ssa.get_variable(op1_register, offset_2)[2] in phi_node_variables:
                operand_2 = phi_node_representation
                variable_operand_2 = Operand(
                    type=OperandType.VARIABLE,
                    value=[variable.name for variable in phi_node_variables],
                )
            else:
                operand_2 = self.ssa.get_variable(op1_register, offset_2)[1]
                variable_operand_2 = Operand(type=OperandType.VARIABLE, value=[operand_2])

            operator = Operator.ADDITION if op in ["+", "-"] else Operator.MULTIPLICATION
            # Set variable value
            if variable[2].value is None and not self.assertion:
                variable[2].value = VariableValue(
                    type=VariableValueType.ABSOLUTE,
                    operation=[variable_operand_1, operator, variable_operand_2],
                )
            source_code += self.print_instruction_decomp(
                f"{is_assert}{variable[1]} {equal} {operand_1} {op} {operand_2}",
                color=utils.color.GREEN,
            )
        # <variable> = <variable> +/- <integer>
        else:
            variable = self.ssa.get_variable(destination_register, destination_offset)
            if variable[2].value is not None or self.assertion:
                is_assert = "assert "
            try:
                value = int(utils.field_element_repr(int(instruction.imm), instruction.prime))
                integer_value = value
                if value < 0 and op == "+":
                    op = "-"
                    value = -value
            except Exception:
                value = instruction.imm

            if self.ssa.get_variable(op0_register, offset_1)[2] in phi_node_variables:
                operand = phi_node_representation
                variable_operand_1 = Operand(
                    type=OperandType.VARIABLE,
                    value=[variable.name for variable in phi_node_variables],
                )
            elif (
                self.block_new_variables == 0
                and len(self.current_function.cfg.parents(self.current_basic_block)) != 0
                and not is_assert
            ):
                if len(phi_node_variables) > 1:
                    operand = phi_node_representation
                    variable_operand_1 = Operand(
                        type=OperandType.VARIABLE,
                        value=[variable.name for variable in phi_node_variables],
                    )
                else:
                    operand = self.ssa.get_variable(op0_register, offset_1)[1]
                    variable_operand_1 = Operand(type=OperandType.VARIABLE, value=[operand])
            else:
                operand = self.ssa.get_variable(op0_register, offset_1)[1]
                variable_operand_1 = Operand(type=OperandType.VARIABLE, value=[operand])

            operator = Operator.ADDITION if op in ["+", "-"] else Operator.MULTIPLICATION
            try:
                variable_operand_2 = Operand(type=OperandType.INTEGER, value=integer_value)
                # Set variable value
                if variable[2].value is None and not self.assertion:
                    variable[2].value = VariableValue(
                        type=VariableValueType.ABSOLUTE,
                        operation=[variable_operand_1, operator, variable_operand_2],
                    )
            except:
                pass

            source_code += self.print_instruction_decomp(
                f"{is_assert}{variable[1]} {equal} {operand} {op} {value}",
                color=utils.color.GREEN,
            )
            self.block_new_variables += 1

    # Set variable function (scope for local variables)
    variable[2].function = self.current_function
    # Set variable basic block ID for the symbolic execution
    variable[2].basic_block_id = self.current_basic_block.id

    if assertion:
        self.assertions.append(assertion)

    return source_code


def _handle_nop_decomp(self, instruction: Instruction) -> str:
    """Handle the NOP opcode
    Args:
            instruction (Instruction): intruction to decompile
    Returns:
        String: The formated NOP instruction
    """
    source_code = ""

    destination_offset = int(instruction.offDest) if instruction.offDest else 0
    if "REGULAR" not in instruction.pcUpdate:
        if instruction.pcUpdate == "JNZ":
            tested_variable = self.ssa.get_variable("ap", destination_offset)
            self.current_basic_block.condition_variable = tested_variable[2]
            source_code += (
                self.print_instruction_decomp(f"if ", color=utils.color.RED)
                + f"({tested_variable[1]} == 0) {{"
            )

            tested_variable[2].function = self.current_function
            self.tab_count += 1
            self.ifcount += 1
            # Detect if there is an else later
            jump_to = int(utils.field_element_repr(int(instruction.imm), instruction.prime)) + int(
                instruction.id
            )
            for inst in self.decompiled_function.instructions:
                if int(inst.id) == int(jump_to) - 2 or int(inst.id) == int(jump_to) - 1:
                    if inst.pcUpdate != "JUMP_REL":
                        self.end_if = int(jump_to)
                        self.ifcount -= 1
        elif instruction.pcUpdate == "JUMP_REL" and instruction.imm != "None":
            if self.ifcount != 0:
                self.tab_count -= 1
                source_code += self.print_instruction_decomp("else:", color=utils.color.RED)
                self.tab_count += 1
                self.end_else.append(
                    int(utils.field_element_repr(int(instruction.imm), instruction.prime))
                    + int(instruction.id)
                )
                self.ifcount -= 1
            else:
                source_code += self.print_instruction_decomp(f"jmp rel {instruction.imm}")

    # dw statements
    elif instruction.hint is None and instruction.imm == "None":
        try:
            dw_value = int(instruction.off3)
            source_code += self.print_instruction_decomp(f"dw {dw_value}", color=utils.color.BLUE)
        except Exception:
            pass
    return source_code


def _handle_call_decomp(self, instruction: Instruction) -> str:
    """Handle the CALL opcode
    Args:
            instruction (Instruction): intruction to decompile
    Returns:
        String: The formated CALL instruction
    """
    # Direct CALL or Relative CALL
    source_code = ""

    call_type = "call abs" if instruction.is_call_abs() else "call rel"
    if instruction.is_call_direct():
        offset = int(utils.field_element_repr(int(instruction.imm), instruction.prime))
        # direct CALL to a fonction
        if instruction.call_xref_func_name is not None:
            call_name = instruction.call_xref_func_name.split(".")
            args = 0
            for function in self.functions:
                if function.name == instruction.call_xref_func_name:
                    if function.args != None:
                        args += len(function.args)

                    called_function = function
                    function_return_values = function.arguments_list(
                        explicit=False, implicit=False, ret=True
                    )

            args_str = ""
            args_list = []
            while args >= 1:
                phi_node_variables = []
                # Generate the phi function representation
                if self.current_basic_block.is_phi_node and not self.first_pass:
                    phi_node_variables = self.get_phi_node_variables()
                    variables_names = [variable.name for variable in self.get_phi_node_variables()]
                    # Phi function is represented in the form Φ(var1, var2, ..., var<n>)
                    phi_node_representation = "Φ(%s)" % ", ".join(variables_names)
                if self.ssa.get_variable("ap", -1 * int(args))[2] in phi_node_variables:
                    args_str += f"{phi_node_representation}"
                    args_list.append(phi_node_variables)
                else:
                    argument_value = self.ssa.get_variable("ap", -1 * int(args))
                    args_str += f"{argument_value[1]}"
                    args_list.append([argument_value])
                if args != 1:
                    args_str += ", "
                args -= 1

            for return_value in function_return_values:
                self.ssa.new_variable(
                    variable_name=return_value, function=called_function, function_result=True
                )
                self.ssa.ap_position += 1

            if function_return_values:
                assigned_variables_list = []
                for i in range(1, len(function_return_values) + 1):
                    assigned_variable = self.ssa.get_variable("ap", -1 * i)[2]
                    assigned_variable.function = self.current_function
                    assigned_variable.basic_block_id = self.current_basic_block.id
                    assigned_variable.value = VariableValue(
                        type=VariableValueType.FUNCTION_CALL,
                        operation=FunctionCall(
                            function=called_function,
                            return_value_position=i - 1,
                            arguments=args_list,
                            call_number=self.function_calls,
                        ),
                    )
                    assigned_variables_list.append(assigned_variable.name)

                assigned_variables = "(%s)" % ", ".join(assigned_variables_list)

                source_code += self.print_instruction_decomp(
                    f"let {assigned_variables} = ", color=utils.color.GREEN
                )
                source_code += (
                    self.print_instruction_decomp(
                        f"{call_name[-1]}", color=utils.color.RED, tab_count=0
                    )
                    + f"({args_str})"
                )
            else:
                source_code += (
                    self.print_instruction_decomp(f"{call_name[-1]}", color=utils.color.RED)
                    + f"({args_str})"
                )
            self.function_calls += 1
        # CALL to a label
        # e.g. call rel (123)
        else:
            source_code += self.print_instruction_decomp(
                f"{call_type} ({offset})", color=utils.color.RED
            )
            if str(offset) in instruction.labels:
                source_code += self.print_instruction_decomp(
                    f"// {instruction.labels[str(offset)]}",
                    color=utils.color.CYAN,
                )
    # CALL
    # e.g. call rel [fp + 4]
    elif instruction.is_call_indirect():
        source_code += self.print_instruction_decomp(
            f"{call_type} [{instruction.op1Addr}{instruction.off2}]"
        )
    else:
        raise NotImplementedError
    return source_code


def _handle_ret_decomp(self, last: bool = False) -> str:
    """Handle the RET opcode
    Args:
        last (Instruction): intruction to decompile
    Returns:
        String: The formated RET instruction
    """
    source_code = ""

    if self.return_values == None:
        source_code += self.print_instruction_decomp("ret", end="\n", color=utils.color.RED)
        if last:
            self.tab_count -= 1
    else:
        idx = len(self.return_values)
        source_code += self.print_instruction_decomp("return", color=utils.color.RED) + "("
        while idx:
            return_variable = self.ssa.get_variable("ap", -1 * int(idx))
            return_variable[2].is_function_return_value = True
            source_code += f"{return_variable[1]}"
            if idx != 1:
                source_code += ", "
            idx -= 1
        source_code += ")\n"
    if last:
        self.tab_count = 0
        source_code += self.print_instruction_decomp("}", color=utils.color.ENDC)
    return source_code


def _handle_hint_decomp(self, instruction: Instruction) -> str:
    """Handle the hint
    Args:
        instruction (Instruction): intruction to decompile
    Returns:
        String: The formated hint
    """
    source_code = ""

    hints = instruction.hint.split("\n")
    source_code += self.print_instruction_decomp("%{ ", end="\n")
    self.tab_count += 1
    for hint in hints:
        source_code += self.print_instruction_decomp(hint, end="\n")
    self.tab_count -= 1
    source_code += self.print_instruction_decomp("%} ", end="\n")
    return source_code
