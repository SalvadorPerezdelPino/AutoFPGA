from hardware.drivers.base_driver import DeviceDriver

class ASICDriver(DeviceDriver):
    def prepare_hardware(self, params: dict) -> None:
        # TODO: Modify .v parameter file using params
        #update_verilog_parameters(params) 
        pass

    def build(self) -> None:
        self.compiler.compile_all()

    def run_simulation(self) -> None:
        pass