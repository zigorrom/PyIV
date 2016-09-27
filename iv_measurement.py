import visa
import keithley24xx

class IVmeasurement:
    def __init__(self,data_storage):
        self.data_storage = data_storage

    def initialize(gateInstr_resource, drainInstr_resource):
        self.gateInstr = Keithley24XX(gateInstr_resource)
        self.drainInstr = Keithley24XX(drainInstr_resource)
    
    def configure(self, config):
        pass

    def run(self):
        pass
