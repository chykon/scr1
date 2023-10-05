from typing import Any
from random import randrange, choice

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge

from ialu_model.ialu import IALU


@cocotb.test()
async def random_test(dut: Any):
    """Testing using random test vectors."""
    cocotb.start_soon(Clock(dut.clk, 2).start(start_high=False))

    await FallingEdge(dut.clk)

    FAST_MUL = True

    ialu = IALU(rvm_ext=True, fast_mul=FAST_MUL)

    # Reset check.

    ialu.set_input_op1(0)
    ialu.set_input_op2(0)
    ialu.set_input_cmd(IALU.Cmd.NONE)
    ialu.set_input_rst_n(0)
    ialu.set_input_rvm_cmd_vd(0)

    dut.rst_n.value = 0
    dut.exu2ialu_main_op1_i.value = 0
    dut.exu2ialu_main_op2_i.value = 0
    dut.exu2ialu_cmd_i.value = IALU.Cmd.NONE.value
    dut.exu2ialu_rvm_cmd_vd_i.value = 0

    ialu.tick()
    await FallingEdge(dut.clk)

    assert dut.ialu2exu_main_res_o.value == ialu.get_output_res()
    assert dut.ialu2exu_rvm_res_rdy_o.value == ialu.get_output_rvm_res_rdy()

    ialu.set_input_rst_n(1)
    dut.rst_n.value = 1

    # Random check.

    # Number of test vectors generated.
    TEST_COUNT = 100

    for _ in range(TEST_COUNT):
        cmd = choice(list(IALU.Cmd))

        OP1 = randrange(2**IALU.XLEN)
        OP2 = randrange(2**IALU.XLEN)

        match cmd:
            case IALU.Cmd.NONE:
                ialu.set_input_cmd(IALU.Cmd.NONE)

                dut.exu2ialu_cmd_i.value = IALU.Cmd.NONE.value

                ialu.tick()
                await FallingEdge(dut.clk)

            case IALU.Cmd.ADD:
                ialu.set_input_op1(OP1)
                ialu.set_input_op2(OP2)
                ialu.set_input_cmd(IALU.Cmd.ADD)

                dut.exu2ialu_main_op1_i.value = OP1
                dut.exu2ialu_main_op2_i.value = OP2
                dut.exu2ialu_cmd_i.value = IALU.Cmd.ADD.value

                ialu.tick()
                await FallingEdge(dut.clk)

                assert dut.ialu2exu_main_res_o.value == ialu.get_output_res()
                assert dut.ialu2exu_rvm_res_rdy_o.value == ialu.get_output_rvm_res_rdy()

            case IALU.Cmd.SUB:
                ialu.set_input_op1(OP1)
                ialu.set_input_op2(OP2)
                ialu.set_input_cmd(IALU.Cmd.SUB)

                dut.exu2ialu_main_op1_i.value = OP1
                dut.exu2ialu_main_op2_i.value = OP2
                dut.exu2ialu_cmd_i.value = IALU.Cmd.SUB.value

                ialu.tick()
                await FallingEdge(dut.clk)

                assert dut.ialu2exu_main_res_o.value == ialu.get_output_res()
                assert dut.ialu2exu_rvm_res_rdy_o.value == ialu.get_output_rvm_res_rdy()

            case IALU.Cmd.MUL:
                if not FAST_MUL:
                    raise

                ialu.set_input_op1(OP1)
                ialu.set_input_op2(OP2)
                ialu.set_input_cmd(IALU.Cmd.MUL)

                dut.exu2ialu_main_op1_i.value = OP1
                dut.exu2ialu_main_op2_i.value = OP2
                dut.exu2ialu_cmd_i.value = IALU.Cmd.MUL.value

                ialu.tick()
                await FallingEdge(dut.clk)

                assert dut.ialu2exu_main_res_o.value == ialu.get_output_res()
                assert dut.ialu2exu_rvm_res_rdy_o.value == ialu.get_output_rvm_res_rdy()

            case IALU.Cmd.DIV:
                ialu.set_input_op1(OP1)
                ialu.set_input_op2(OP2)
                ialu.set_input_cmd(IALU.Cmd.DIV)
                ialu.set_input_rvm_cmd_vd(1)

                dut.exu2ialu_main_op1_i.value = OP1
                dut.exu2ialu_main_op2_i.value = OP2
                dut.exu2ialu_cmd_i.value = IALU.Cmd.DIV.value
                dut.exu2ialu_rvm_cmd_vd_i.value = 1

                MAX_DIV_DELAY = 33

                for _ in range(MAX_DIV_DELAY):
                    ialu.tick()
                    await FallingEdge(dut.clk)

                    if dut.ialu2exu_rvm_res_rdy_o.value:
                        for _ in range(MAX_DIV_DELAY):
                            if ialu.get_output_rvm_res_rdy():
                                break
                            else:
                                ialu.tick()
                        break

                    if ialu.get_output_rvm_res_rdy():
                        for _ in range(MAX_DIV_DELAY):
                            if dut.ialu2exu_rvm_res_rdy_o.value:
                                break
                            else:
                                await FallingEdge(dut.clk)
                        break

                assert dut.ialu2exu_main_res_o.value == ialu.get_output_res()
                assert (
                    dut.ialu2exu_rvm_res_rdy_o.value
                    == ialu.get_output_rvm_res_rdy()
                    == 1
                )

                ialu.set_input_rvm_cmd_vd(0)
                dut.exu2ialu_rvm_cmd_vd_i.value = 0

                # One clock cycle of additional delay of the `DIV` operation required to avoid
                # an invalid signal at the output of `ialu2exu_rvm_res_rdy_o`.
                dut.exu2ialu_cmd_i.value = IALU.Cmd.NONE.value
                await FallingEdge(dut.clk)
