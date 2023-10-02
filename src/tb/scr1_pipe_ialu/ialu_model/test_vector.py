from ialu import IALU


class TestVector:
    """IALU model test vector template."""

    def __init__(
        self,
        *,
        # inputs
        op1: int | None = None,
        op2: int | None = None,
        cmd: IALU.Cmd | None = None,
        rst_n: int | None = None,
        rvm_cmd_vd: int | None = None,
        # outputs
        res: int | None = None,
        rvm_res_rdy: int | None = None,
        # other
        delay: int = 1,
    ):
        """
        Create an instance of the IALU model test vector.

        Parameters:

        Test input values:
        * `op1`: main ALU 1st operand
        * `op2`: main ALU 2nd operand
        * `cmd`: IALU command
        * `rst_n`: IALU reset
        * `rvm_cmd_vd`: MUL/DIV command valid

        Expected outputs:
        * `res`: main ALU result
        * `rvm_res_rdy`: MUL/DIV result ready

        Other:
        * `delay`: delay in receiving the result (for synchronous sequential logic)
        """
        super().__init__()

        self.OP1 = op1
        self.OP2 = op2
        self.CMD = cmd
        self.RST_N = rst_n
        self.RVM_CMD_VD = rvm_cmd_vd

        self.RES = res
        self.RVM_RES_RDY = rvm_res_rdy

        self.DELAY = delay
