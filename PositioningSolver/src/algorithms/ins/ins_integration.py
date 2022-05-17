from PositioningSolver.src.algorithms.ins.ins_alg import InsAlgorithm


class FreeIntegrationAlg(InsAlgorithm):
    def __init__(self, initial_pos, initial_vel):
        super().__init__()
        self.inputs = ["time", "gyro", "accel"]
        self.outputs = ["ref_gyro", "ref_accel", "gyro", "accel", "gps_ecef", "gps"]

        # TODO save initial state

    def __str__(self):
        return "InsAlgorithm(Free Integration)"

    def compute(self, time, gyro, accel):
        print(time)
