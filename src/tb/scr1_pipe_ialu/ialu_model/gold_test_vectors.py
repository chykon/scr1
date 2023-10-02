from enum import Enum

from ialu import IALU
from test_vector import TestVector


class GoldTestVectorGroup(Enum):
    """Groups of reference test vectors."""

    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3


GOLD_TEST_VECTORS = {
    GoldTestVectorGroup.ADD: [
        TestVector(
            op1=2**IALU.XLEN - 1,
            op2=2**IALU.XLEN - 1,
            cmd=IALU.Cmd.ADD,
            res=2**IALU.XLEN - 2,
        ),
        TestVector(
            op1=0b01010101010101010101010101010101,
            op2=0b10101010101010101010101010101010,
            cmd=IALU.Cmd.ADD,
            res=2**IALU.XLEN - 1,
        ),
        TestVector(
            op1=0,
            op2=0,
            cmd=IALU.Cmd.ADD,
            res=0,
        ),
        TestVector(
            op1=0b10101010101010101010101010101010,
            op2=0b01010101010101010101010101010101,
            cmd=IALU.Cmd.ADD,
            res=2**IALU.XLEN - 1,
        ),
    ],
    GoldTestVectorGroup.SUB: [
        TestVector(
            op1=0b01010101010101010101010101010101,
            op2=0b10101010101010101010101010101010,
            cmd=IALU.Cmd.SUB,
            res=0b10101010101010101010101010101011,
        ),
        TestVector(
            op1=2**IALU.XLEN - 1,
            op2=2**IALU.XLEN - 1,
            cmd=IALU.Cmd.SUB,
            res=0,
        ),
        TestVector(
            op1=0b10101010101010101010101010101010,
            op2=0b01010101010101010101010101010101,
            cmd=IALU.Cmd.SUB,
            res=0b01010101010101010101010101010101,
        ),
        TestVector(
            op1=0,
            op2=0,
            cmd=IALU.Cmd.SUB,
            res=0,
        ),
    ],
    GoldTestVectorGroup.MUL: [
        TestVector(
            op1=2**IALU.XLEN - 1,
            op2=2**IALU.XLEN - 1,
            cmd=IALU.Cmd.MUL,
            rvm_cmd_vd=1,
            res=1,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=0,
            op2=0,
            cmd=IALU.Cmd.MUL,
            rvm_cmd_vd=1,
            res=0,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=0b01010101010101010101010101010101,
            op2=0b10101010101010101010101010101010,
            cmd=IALU.Cmd.MUL,
            rvm_cmd_vd=1,
            res=0b01110001110001110001110001110010,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=2**IALU.XLEN - 1,
            op2=0,
            cmd=IALU.Cmd.MUL,
            rvm_cmd_vd=1,
            res=0,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=0b10101010101010101010101010101010,
            op2=0b01010101010101010101010101010101,
            cmd=IALU.Cmd.MUL,
            rvm_cmd_vd=1,
            res=0b01110001110001110001110001110010,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=0,
            op2=2**IALU.XLEN - 1,
            cmd=IALU.Cmd.MUL,
            rvm_cmd_vd=1,
            res=0,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
    ],
    GoldTestVectorGroup.DIV: [
        TestVector(
            op1=2**IALU.XLEN - 1,
            op2=2**IALU.XLEN - 1,
            cmd=IALU.Cmd.DIV,
            rvm_cmd_vd=1,
            res=1,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=0,
            op2=0,
            cmd=IALU.Cmd.DIV,
            rvm_cmd_vd=1,
            res=2**IALU.XLEN - 1,
            rvm_res_rdy=1,
        ),
        TestVector(
            op1=0b01010101010101010101010101010101,
            op2=0b10101010101010101010101010101010,
            cmd=IALU.Cmd.DIV,
            rvm_cmd_vd=1,
            res=0,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=2**IALU.XLEN - 1,
            op2=0,
            cmd=IALU.Cmd.DIV,
            rvm_cmd_vd=1,
            res=2**IALU.XLEN - 1,
            rvm_res_rdy=1,
        ),
        TestVector(
            op1=0b10101010101010101010101010101010,
            op2=0b01010101010101010101010101010101,
            cmd=IALU.Cmd.DIV,
            rvm_cmd_vd=1,
            res=2,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=0,
            op2=2**IALU.XLEN - 1,
            cmd=IALU.Cmd.DIV,
            rvm_cmd_vd=1,
            res=0,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=2**IALU.XLEN - 1,
            op2=1,
            cmd=IALU.Cmd.DIV,
            rvm_cmd_vd=1,
            res=2**IALU.XLEN - 1,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=0b10000000000000000000000000000000,
            op2=2**IALU.XLEN - 1,
            cmd=IALU.Cmd.DIV,
            rvm_cmd_vd=1,
            res=0,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
        TestVector(
            op1=0b01111111111111111111111111111111,
            op2=1,
            cmd=IALU.Cmd.DIV,
            rvm_cmd_vd=1,
            res=0b01111111111111111111111111111111,
            rvm_res_rdy=1,
            delay=IALU.RVM_DELAY,
        ),
    ],
}
"""A set of reference test vectors for the IALU model."""
