from typing import Any
from random import randrange, choice

import cocotb
from cocotb.clock import Clock
from cocotb.runner import get_runner
from cocotb.triggers import FallingEdge

import ialu_model.test
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


def run(check_model: bool = True):
    # Model testing.
    if check_model:
        ialu_model.test.run()

    runner = get_runner("verilator")

    runner.build(
        verilog_sources=["src/core/pipeline/scr1_pipe_ialu.sv"],
        includes=["src/includes"],
        hdl_toplevel="scr1_pipe_ialu",
        build_args=[
            "-Wall",
            "-Wpedantic",
            "-Wno-WIDTHEXPAND",
            "-Wno-CASEINCOMPLETE",
            "-Wno-EOFNEWLINE",
            "-Wno-VARHIDDEN",
            "-Wno-UNUSEDPARAM",
            "--assert",
            "--trace",
        ],
    )

    # Argument '+verilator+seed+' must be an unsigned integer,
    # greater than 0, less than 2147483648
    SEED = randrange(2147483647) + 1

    runner.test(
        hdl_toplevel="scr1_pipe_ialu",
        test_module="ialu_test",
        seed=SEED,
        plusargs=[
            f"+verilator+seed+{SEED}",
            "+verilator+rand+reset+2",
        ],
    )


if __name__ == "__main__":
    run()
