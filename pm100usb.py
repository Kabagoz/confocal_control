""" This module contains the PM100USB class and its related functions, which
implement simultaneous initialization and control of a
Thorlabs PM100USB Powermeter head.

Classes, Exceptions and Functions:
class PM100USB --     initialization and control of the 3 channels of a
                    Thorlabs PM100USB

@author: Begum Kabagoz, 2022, Boston University
"""

import pyvisa as visa
from ThorlabsPM100 import ThorlabsPM100



class PM100USB:
    def __init__(self, device_ID):
        rm = visa.ResourceManager()
        print(rm.list_resources())
        self.power_meter = None
        try:
            # inst = rm.open_resource('USB0::0x1313::0x8072::P2006395::INSTR', timeout=1)
            address = f'USB0::0x1313::0x8072::{device_ID}::INSTR'  # this is for PM100USB
            # address = f'USB0::0x1313::0x8078::{device_ID}::INSTR'  # this is for PM100D
            inst = rm.open_resource(address, timeout=1)
            self.power_meter = ThorlabsPM100(inst=inst)
            print("Powermeter connected.")
        except:
            print("Can't find powermeter.")

    def __enter__(self):
        return self

    def get_power_data(self):
        power = self.power_meter.read
        return power

    def set_wavelength(self, wavelength):
        self.power_meter.sense.correction.wavelength = wavelength

    def get_unit(self):
        return self.power_meter.sense.power.dc.unit

    def set_average(self, sample_number=10):
        self.power_meter.sense.average.count = sample_number
        return self.power_meter.sense.average.count

    def get_range(self):
        return (self.power_meter.sense.power.dc.range.minimum_upper,
                self.power_meter.sense.power.dc.range.maximum_upper)

    def set_range(self, power_range):
        (self.power_meter.sense.power.dc.range) = power_range
        return (self.power_meter.sense.power.dc.range.minimum_upper,
                self.power_meter.sense.power.dc.range.maximum_upper)

    def zero(self):
        self.power_meter.sense.correction.collect.zero.initiate()
        return print("Zeroed.")

    # def set_unit(self, unit):
    # self.power_meter.sense.power.dc.unit = unit
    # return self.power_meter.sense.power.dc.unit

    # def beeper(self):
    #     # self.power_meter.system.beeper.immediate
    #     return self.power_meter.system.beeper.state

    def sensor_info(self):
        sensor = self.power_meter.system.sensor.idn
        infos = sensor.split(",")
        model = infos[0]
        serial = infos[1]
        return infos[0], infos[1]

    def shutdown(self):
        print("Shutting the PM100USB down.")
        self.power_meter.abort()
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return True if exc_type is None else False
        # pass


if __name__ == "__main__":
    print("\n")
    device_ID = "P2006395"
    with PM100USB(device_ID) as powermeter:
        data = powermeter.get_power_data()
        print(data)
        [detector_model, detector_serial] = powermeter.sensor_info()
        print(f"Detector model: {detector_model}, Serial: {detector_serial}")

    del powermeter

#
# print(power_meter.read)
#
# wavelengths = range(700, 1000, 50)
#
# for wavelength in wavelengths:
#     power_meter.sense.correction.wavelength = wavelength
#     print(power_meter.read)


# print(power_meter.measure.scalar.temperature())
