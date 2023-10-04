from enum import Enum
from random import randrange, choice
from ctypes import c_uint32

import numpy as np


class IALU:
    """
    Trusted model for IALU hardware unit verification.

    Inputs:
    * `op1`: main ALU 1st operand
    * `op2`: main ALU 2nd operand
    * `cmd`: IALU command
    * `rst_n`: IALU reset
    * `rvm_cmd_vd`: MUL/DIV command valid

    Outputs:
    * `res`: main ALU result
    * `rvm_res_rdy`: MUL/DIV result ready
    """

    class Cmd(Enum):
        """
        Operation codes.

        Delays:
        * `NONE`: 1 tick
        * `ADD`: 1 tick
        * `SUB`: 1 tick
        * `MUL`: fast_mul ? 1 tick : 32 ticks
        * `DIV`: 32 ticks
        """

        NONE = 0
        ADD = 4
        SUB = 5
        MUL = 15
        DIV = 19

    XLEN = 32
    """Width of output values."""

    RVM_DELAY = 32
    """Delay in execution of MUL/DIV operations."""

    def __init__(self, rvm_ext: bool = False, fast_mul: bool = False):
        """
        Create an instance of the model.

        Parameters:

        * `rvm_ext`: support for multiplication/division operations (RISC-V "M" extension)
        * `fast_mul`: support for fast multiplication (pure combinational logic)
        """
        super().__init__()

        # `fast_mul` requires `rvm_ext`.
        assert not (not rvm_ext and fast_mul)

        self._RVM_EXT = rvm_ext
        self._FAST_MUL = fast_mul

        self._op1 = randrange(2**self.XLEN)
        self._op2 = randrange(2**self.XLEN)
        self._cmd = choice(list(IALU.Cmd))
        self._res = randrange(2**self.XLEN)

        self._rst_n = randrange(2)
        self._rvm_cmd_vd = randrange(2)
        self._rvm_res_rdy = randrange(2)

        self._rvm_op1 = randrange(2**self.XLEN)
        self._rvm_op2 = randrange(2**self.XLEN)
        self._rvm_cmd = choice(list(IALU.Cmd))
        self._rvm_delay_counter = randrange(self.RVM_DELAY)

    def tick(self):
        """Update model state."""
        if not self._rst_n:
            self._rvm_res_rdy = 1
            self._rvm_delay_counter = 0
            result = 0
        else:
            match self._cmd:
                case IALU.Cmd.NONE:
                    assert self._rvm_cmd_vd == 0
                    result = self._res

                case IALU.Cmd.ADD:
                    assert self._rvm_cmd_vd == 0
                    result = self._op1 + self._op2

                case IALU.Cmd.SUB:
                    assert self._rvm_cmd_vd == 0
                    result = self._op1 - self._op2

                case IALU.Cmd.MUL | IALU.Cmd.DIV:
                    if not self._RVM_EXT:
                        raise

                    if (self._cmd == IALU.Cmd.MUL) and self._FAST_MUL:
                        result = self._op1 * self._op2
                    elif self._rvm_cmd_vd:
                        if self._rvm_delay_counter == 0:
                            self._rvm_op1 = self._op1
                            self._rvm_op2 = self._op2
                            self._rvm_cmd = self._cmd

                        # If `rvm_cmd_vd` is set, then the operands and opcode should
                        # not change until the current operation completes.
                        assert self._rvm_op1 == self._op1
                        assert self._rvm_op2 == self._op2
                        assert self._rvm_cmd == self._cmd

                        is_division_by_zero = (self._cmd == IALU.Cmd.DIV) and (
                            self._op2 == 0
                        )

                        is_ops_equal = self._op1 == self._op2

                        if (
                            (
                                self._rvm_delay_counter
                                < (
                                    self.RVM_DELAY - 2
                                    if is_ops_equal
                                    else self.RVM_DELAY - 1
                                )
                            )
                            and not ((self._op1 == 0) or (self._op2 == 0))
                            and not is_division_by_zero
                        ):
                            self._rvm_delay_counter += 1
                            self._rvm_res_rdy = 0
                            result = self._res
                        else:
                            self._rvm_delay_counter = 0
                            self._rvm_res_rdy = 1
                            match self._cmd:
                                case IALU.Cmd.MUL:
                                    result = self._op1 * self._op2
                                case IALU.Cmd.DIV:
                                    if self._op2 == 0:
                                        result = 2**self.XLEN - 1
                                    else:
                                        result = np.int32(
                                            np.array(self._op1).astype(np.int32)
                                            / np.array(self._op2).astype(np.int32)
                                        ).item()
                    else:
                        result = self._res

        self._res = c_uint32(result).value

    # Main Adder inputs/outputs

    def set_input_op1(self, value: int):
        """Place `value` into input `op1`."""
        self._op1 = value

    def set_input_op2(self, value: int):
        """Place `value` into input `op2`."""
        self._op2 = value

    def set_input_cmd(self, value: Cmd):
        """Place `value` into input `cmd`."""
        self._cmd = value

    def get_output_res(self):
        """Return the value of the output `res`."""
        return self._res

    # MUL/DIV inputs/outputs

    def set_input_rst_n(self, value: int):
        """Place `value` into input `rst_n`."""
        self._rst_n = value

    def set_input_rvm_cmd_vd(self, value: int):
        """Place `value` into input `rvm_cmd_vd`."""
        self._rvm_cmd_vd = value

    def get_output_rvm_res_rdy(self):
        """Return the value of the output `rvm_res_rdy`."""
        return self._rvm_res_rdy
