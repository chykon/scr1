from ialu import IALU
from gold_test_vectors import GOLD_TEST_VECTORS, GoldTestVectorGroup


def _test():
    ialu = IALU(rvm_ext=True)

    ialu.set_input_rst_n(0)
    ialu.tick()
    ialu.set_input_rvm_cmd_vd(0)
    ialu.set_input_rst_n(1)

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

                    for _ in range(test_vector.DELAY):
                        ialu.tick()

                    assert ialu.get_output_res() == test_vector.RES

                case GoldTestVectorGroup.MUL | GoldTestVectorGroup.DIV:
                    assert test_vector.OP1 is not None
                    assert test_vector.OP2 is not None
                    assert test_vector.CMD is not None
                    assert test_vector.RVM_CMD_VD is not None

                    ialu.set_input_op1(test_vector.OP1)
                    ialu.set_input_op2(test_vector.OP2)
                    ialu.set_input_cmd(test_vector.CMD)
                    ialu.set_input_rvm_cmd_vd(test_vector.RVM_CMD_VD)

                    for _ in range(test_vector.DELAY):
                        ialu.tick()
                        if _ < (test_vector.DELAY - 1):
                            assert ialu.get_output_rvm_res_rdy() == 0

                    assert ialu.get_output_res() == test_vector.RES
                    assert ialu.get_output_rvm_res_rdy() == test_vector.RVM_RES_RDY


if __name__ == "__main__":
    _test()
