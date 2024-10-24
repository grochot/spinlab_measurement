import json
import os
import sys


class SaveParameters:

    def __init__(self):
        pass

    def get_executable_path(self):
        if getattr(sys, "frozen", False):
            # Jeśli jest to wersja skompilowana przez PyInstaller
            return os.path.dirname(sys.executable) + "/logic"
        else:
            # Jeśli jest to wersja uruchamiana z kodu źródłowego
            return os.path.dirname(os.path.abspath(__file__))

    def WriteFile(self, data, file_path, filename):
        # Znajdź lokalizację pliku exe
        executable_path = self.get_executable_path()

        # Stwórz nazwę pliku logów
        parameters_file_path = os.path.join(executable_path, "parameters.json")
        data["path"] = file_path
        data["filename"] = filename
        json_object = json.dumps(data, indent=4)
        with open(parameters_file_path, "w") as outfile:
            outfile.write(json_object)

    def ReadFile(self):
        # Znajdź lokalizację pliku exe
        executable_path = self.get_executable_path()

        # Stwórz nazwę pliku logów
        parameters_file_path = os.path.join(executable_path, "parameters.json")
        try:
            with open(parameters_file_path, "r") as openfile:
                json_object = json.load(openfile)
            return json_object
        except:
            json_object = """{
    "mode": "HarmonicMode",
    "sample_name": "dfsdf",
    "vector": "1,5,100",
    "mode_resistance": false,
    "mode_fmr": "const H",
    "set_sourcemeter": "none",
    "set_multimeter": "none",
    "set_pulsegenerator": "Agilent 2912",
    "set_gaussmeter": "none",
    "set_field": "none",
    "set_lockin": "SR830",
    "set_automaticstation": false,
    "set_rotationstation": true,
    "set_switch": false,
    "set_kriostat": false,
    "set_lfgen": "none",
    "set_analyzer": "VectorAnalyzer",
    "set_generator": "Agilent",
    "address_sourcemeter": "None",
    "address_multimeter": "None",
    "address_daq": "Dev4/ao0",
    "address_gaussmeter": "None",
    "address_lockin": "None",
    "address_switch": "None",
    "address_analyzer": "None",
    "address_generator": "None",
    "address_lfgen": "None",
    "address_pulsegenerator": "None",
    "sourcemter_source": "CURR",
    "sourcemeter_compliance": 0.5,
    "sourcemeter_channel": "Channel A",
    "sourcemeter_limit": 0.0001,
    "sourcemeter_nplc": 0.1,
    "sourcemeter_average": 1,
    "sourcemeter_bias": 1e-05,
    "multimeter_function": "DCV",
    "multimeter_resolution": 1e-06,
    "multimeter_nplc": 10,
    "multimeter_autorange": true,
    "multimeter_range": 10.0,
    "multimeter_average": 1,
    "field_constant": -0.00246145,
    "gaussmeter_range": 4,
    "gaussmeter_resolution": "4 digits",
    "lockin_average": 20,
    "lockin_input_coupling": "AC",
    "lockin_reference_source": "Internal",
    "lockin_dynamic_reserve": "Normal",
    "lockin_input_connection": "A",
    "lockin_sensitivity": "20 uV/pA",
    "lockin_frequency": 384.0,
    "lockin_harmonic": 1,
    "lockin_sine_amplitude": 1.0,
    "lockin_timeconstant": "300 ms",
    "lockin_channel1": "R",
    "lockin_channel2": "Theta",
    "lockin_autophase": false,
    "generator_frequency": 4000000000.0,
    "generator_power": 12.0,
    "lfgen_freq": 330.0,
    "lfgen_amp": 2.0,
    "set_field_value_fmr": 0.0,
    "field_step": 100.0,
    "delay_field": 0.25,
    "delay_lockin": 1.0,
    "delay_bias": 2.0,
    "rotation_axis": "Azimuthal",
    "rotation_polar_constant": 90.0,
    "rotation_azimuth_constant": 40.0,
    "constant_field_value": 2.2222222222222223,
    "address_rotationstation": "COM4",
    "mode_cims_relays": false,
    "pulsegenerator_offset": 0.0,
    "pulsegenerator_duration": 0.001,
    "pulsegenerator_pulsetype": "VOLT",
    "pulsegenerator_channel": "Channel A",
    "delay_measurement": 0.25,
    "pulsegenerator_compliance": 0.5,
    "pulsegenerator_source_range": 5.0,
    "return_the_rotationstation": true,
    "field_bias_value": 0.0,
    "remagnetization": true,
    "remagnetization_value": -300.0,
    "remagnetization_time": 1.0,
    "hold_the_field_after_measurement": false,
    "remanency_correction": true,
    "set_polar_angle": 0.0,
    "set_azimuthal_angle": 90.0,
    "remanency_correction_time": 5.0,
    "layout_type": true,
    "path": "C://",
    "filename": "DATA"
}"""
        with open(parameters_file_path, "w") as outfile:
            outfile.write(json_object)
            outfile.close()

        with open(parameters_file_path, "r") as openfile:
            json_object = json.load(openfile)
            openfile.close()
        return json_object
