from typing import Any

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge

from ialu_model.ialu import IALU
from ialu_model.gold_test_vectors import GOLD_TEST_VECTORS, GoldTestVectorGroup


@cocotb.test()
async def basic_test(dut: Any):
    """Basic test using reference test vectors."""
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

    # Basic check.

    for test_group in GOLD_TEST_VECTORS:
        for test_vector in GOLD_TEST_VECTORS[test_group]:
            match test_group:
                case GoldTestVectorGroup.ADD | GoldTestVectorGroup.SUB:
                    assert test_vector.OP1 is not None
                    assert test_vector.OP2 is not None
                    assert test_vector.CMD is not None

                    ialu.set_input_op1(test_vector.OP1)
                    ialu.set_input_op2(test_vector.OP2)
                    ialu.set_input_cmd(test_vector.CMD)

                    dut.exu2ialu_main_op1_i.value = test_vector.OP1
                    dut.exu2ialu_main_op2_i.value = test_vector.OP2
                    dut.exu2ialu_cmd_i.value = test_vector.CMD.value

                    for _ in range(test_vector.DELAY):
                        ialu.tick()
                        await FallingEdge(dut.clk)

                    assert (
                        dut.ialu2exu_main_res_o.value
                        == ialu.get_output_res()
                        == test_vector.RES
                    )
                    assert (
                        dut.ialu2exu_rvm_res_rdy_o.value
                        == ialu.get_output_rvm_res_rdy()
                        == 1
                    )

                case GoldTestVectorGroup.MUL | GoldTestVectorGroup.DIV:
                    assert test_vector.OP1 is not None
                    assert test_vector.OP2 is not None
                    assert test_vector.CMD is not None
                    assert test_vector.RVM_CMD_VD is not None

                    ialu.set_input_op1(test_vector.OP1)
                    ialu.set_input_op2(test_vector.OP2)
                    ialu.set_input_cmd(test_vector.CMD)
                    ialu.set_input_rvm_cmd_vd(test_vector.RVM_CMD_VD)

                    dut.exu2ialu_main_op1_i.value = test_vector.OP1
                    dut.exu2ialu_main_op2_i.value = test_vector.OP2
                    dut.exu2ialu_cmd_i.value = test_vector.CMD.value
                    dut.exu2ialu_rvm_cmd_vd_i.value = test_vector.RVM_CMD_VD

                    match test_group:
                        case GoldTestVectorGroup.MUL:
                            if not FAST_MUL:
                                raise
                            ialu.tick()
                            await FallingEdge(dut.clk)

                        case GoldTestVectorGroup.DIV:
                            for _ in range(test_vector.DELAY):
                                ialu.tick()
                                await FallingEdge(dut.clk)

                                if (_ < (test_vector.DELAY - 1)) and (
                                    test_vector.DELAY > 1
                                ):
                                    assert (
                                        dut.ialu2exu_rvm_res_rdy_o.value
                                        == ialu.get_output_rvm_res_rdy()
                                        == 0
                                    )

                    assert (
                        dut.ialu2exu_main_res_o.value
                        == ialu.get_output_res()
                        == test_vector.RES
                    )
                    assert (
                        dut.ialu2exu_rvm_res_rdy_o.value
                        == ialu.get_output_rvm_res_rdy()
                        == test_vector.RVM_RES_RDY
                    )
