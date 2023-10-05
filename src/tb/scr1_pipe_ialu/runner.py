from random import randrange

from cocotb.runner import get_runner

import ialu_model.test


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
            "--coverage",
        ],
    )

    # Argument '+verilator+seed+' must be an unsigned integer,
    # greater than 0, less than 2147483648
    SEED = randrange(2147483647) + 1

    runner.test(
        hdl_toplevel="scr1_pipe_ialu",
        test_module=["ialu_test.basic_test", "ialu_test.random_test"],
        seed=SEED,
        plusargs=[
            f"+verilator+seed+{SEED}",
            "+verilator+rand+reset+2",
        ],
    )


if __name__ == "__main__":
    run()
