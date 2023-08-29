import serial
import re


class TestSensorGainSetting:
    serial_port = serial.Serial()

    @classmethod
    def setup_class(cls):
        cls.serial_port.baudrate = 115200
        cls.serial_port.port = "/dev/ttyACM0"
        cls.serial_port.open()

    @classmethod
    def teardown_class(cls):
        setParameter(cls.serial_port, b"SET_GAIN GAIN_1X")
        cls.serial_port.close()

    def test_gain_initial_status(self):
        data = readStatus(self.serial_port)
        assert data["gain"] == "GAIN_1X"

    def test_gain_set_to_1_33x(self):
        setParameter(self.serial_port, b"SET_GAIN GAIN_1_33X")
        data = readStatus(self.serial_port)
        assert data["gain"] == "GAIN_1_33X"

    def test_gain_set_to_1_67x(self):
        setParameter(self.serial_port, b"SET_GAIN GAIN_1_67X")
        data = readStatus(self.serial_port)
        assert data["gain"] == "GAIN_1_67X"

    def test_gain_set_to_2x(self):
        setParameter(self.serial_port, b"SET_GAIN GAIN_2X")
        data = readStatus(self.serial_port)
        assert data["gain"] == "GAIN_2X"

    def test_gain_set_to_2_5x(self):
        setParameter(self.serial_port, b"SET_GAIN GAIN_2_5X")
        data = readStatus(self.serial_port)
        assert data["gain"] == "GAIN_2_5X"

    def test_gain_set_to_3x(self):
        setParameter(self.serial_port, b"SET_GAIN GAIN_3X")
        data = readStatus(self.serial_port)
        assert data["gain"] == "GAIN_3X"

    def test_gain_set_to_4x(self):
        setParameter(self.serial_port, b"SET_GAIN GAIN_4X")
        data = readStatus(self.serial_port)
        assert data["gain"] == "GAIN_4X"

    def test_gain_set_to_5x(self):
        setParameter(self.serial_port, b"SET_GAIN GAIN_5X")
        data = readStatus(self.serial_port)
        assert data["gain"] == "GAIN_5X"

    def test_gain_set_to_1x(self):
        setParameter(self.serial_port, b"SET_GAIN GAIN_1X")
        data = readStatus(self.serial_port)
        assert data["gain"] == "GAIN_1X"


class TestSensorResolutionSetting:
    serial_port = serial.Serial()

    @classmethod
    def setup_class(cls):
        cls.serial_port.baudrate = 115200
        cls.serial_port.port = "/dev/ttyACM0"
        cls.serial_port.open()

    @classmethod
    def teardown_class(cls):
        setParameter(cls.serial_port, b"SET_RESOLUTION RES_16")
        cls.serial_port.close()

    def test_initial_resolution(self):
        data = readStatus(self.serial_port)
        assert data["resolution"] == "RES_16"

    def test_resolution_set_to_17bit(self):
        setParameter(self.serial_port, b"SET_RESOLUTION RES_17")
        data = readStatus(self.serial_port)
        assert data["resolution"] == "RES_17"

    def test_resolution_set_to_18bit(self):
        setParameter(self.serial_port, b"SET_RESOLUTION RES_18")
        data = readStatus(self.serial_port)
        assert data["resolution"] == "RES_18"

    def test_resolution_set_to_19bit(self):
        setParameter(self.serial_port, b"SET_RESOLUTION RES_19")
        data = readStatus(self.serial_port)
        assert data["resolution"] == "RES_19"

    def test_resolution_set_to_16bit(self):
        setParameter(self.serial_port, b"SET_RESOLUTION RES_16")
        data = readStatus(self.serial_port)
        assert data["resolution"] == "RES_16"


class TestSensorOversamplingSetting:
    serial_port = serial.Serial()

    @classmethod
    def setup_class(cls):
        cls.serial_port.baudrate = 115200
        cls.serial_port.port = "/dev/ttyACM0"
        cls.serial_port.open()

    @classmethod
    def teardown_class(cls):
        setParameter(cls.serial_port, b"SET_OVERSAMPLING OSR_3")
        cls.serial_port.close()

    def test_initial_oversampling(self):
        data = readStatus(self.serial_port)
        assert data["oversampling"] == "OSR_3"

    def test_oversampling_set_to_0(self):
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_0")
        data = readStatus(self.serial_port)
        assert data["oversampling"] == "OSR_0"

    def test_oversampling_set_to_1(self):
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_1")
        data = readStatus(self.serial_port)
        assert data["oversampling"] == "OSR_1"

    def test_oversampling_set_to_2(self):
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_2")
        data = readStatus(self.serial_port)
        assert data["oversampling"] == "OSR_2"

    def test_oversampling_set_to_3(self):
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_3")
        data = readStatus(self.serial_port)
        assert data["oversampling"] == "OSR_3"


class TestSensorFilterSetting:
    serial_port = serial.Serial()

    @classmethod
    def setup_class(cls):
        cls.serial_port.baudrate = 115200
        cls.serial_port.port = "/dev/ttyACM0"
        cls.serial_port.open()

    @classmethod
    def teardown_class(cls):
        setParameter(cls.serial_port, b"SET_FILTER FILTER_7")
        cls.serial_port.close()

    def test_initial_filter(self):
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_7"

    def test_filter_set_to_0(self):
        setParameter(self.serial_port, b"SET_FILTER FILTER_0")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_0"

    def test_filter_set_to_1(self):
        setParameter(self.serial_port, b"SET_FILTER FILTER_1")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_1"

    def test_filter_set_to_2(self):
        setParameter(self.serial_port, b"SET_FILTER FILTER_2")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_2"

    def test_filter_set_to_3(self):
        setParameter(self.serial_port, b"SET_FILTER FILTER_3")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_3"

    def test_filter_set_to_4(self):
        setParameter(self.serial_port, b"SET_FILTER FILTER_4")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_4"

    def test_filter_set_to_5(self):
        setParameter(self.serial_port, b"SET_FILTER FILTER_5")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_5"

    def test_filter_set_to_6(self):
        setParameter(self.serial_port, b"SET_FILTER FILTER_6")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_6"

    def test_filter_set_to_7(self):
        setParameter(self.serial_port, b"SET_FILTER FILTER_7")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_7"


class TestSensorHallConfigurationSetting:
    serial_port = serial.Serial()

    @classmethod
    def setup_class(cls):
        cls.serial_port.baudrate = 115200
        cls.serial_port.port = "/dev/ttyACM0"
        cls.serial_port.open()

    @classmethod
    def teardown_class(cls):
        setParameter(cls.serial_port, b"SET_HALLCONF HC_12")
        cls.serial_port.close()

    def test_initial_hall_config(self):
        data = readStatus(self.serial_port)
        assert data["hallconfig"] == "HC_12"

    def test_hall_config_set_to_0(self):
        setParameter(self.serial_port, b"SET_HALLCONF HC_0")
        data = readStatus(self.serial_port)
        assert data["hallconfig"] == "HC_0"

    def test_hall_config_set_to_12(self):
        setParameter(self.serial_port, b"SET_HALLCONF HC_12")
        data = readStatus(self.serial_port)
        assert data["hallconfig"] == "HC_12"


class TestForbiddenConfigurations:
    serial_port = serial.Serial()

    @classmethod
    def setup_class(cls):
        cls.serial_port.baudrate = 115200
        cls.serial_port.port = "/dev/ttyACM0"
        cls.serial_port.open()

    @classmethod
    def teardown_class(cls):
        setParameter(cls.serial_port, b"SET_GAIN GAIN_1X")
        setParameter(cls.serial_port, b"SET_RESOLUTION RES_16")
        setParameter(cls.serial_port, b"SET_OVERSAMPLING OSR_3")
        setParameter(cls.serial_port, b"SET_FILTER FILTER_7")
        setParameter(cls.serial_port, b"SET_HALLCONF HC_12")
        cls.serial_port.close()

    def test_when_hc_equals_12_and_oversampling_equals_0_then_filter_cant_be_set_to_0(
        self,
    ):
        setParameter(self.serial_port, b"SET_FILTER FILTER_7")
        setParameter(self.serial_port, b"SET_HALLCONF HC_12")
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_0")
        setParameter(self.serial_port, b"SET_FILTER FILTER_0")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_7"

    def test_when_hc_equals_12_and_oversampling_equals_0_then_filter_cant_be_set_to_1(
        self,
    ):
        setParameter(self.serial_port, b"SET_FILTER FILTER_7")
        setParameter(self.serial_port, b"SET_HALLCONF HC_12")
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_0")
        setParameter(self.serial_port, b"SET_FILTER FILTER_1")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_7"

    def test_when_hc_equals_12_and_filter_equals_0_then_oversampling_cant_be_set_to_0(
        self,
    ):
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_3")
        setParameter(self.serial_port, b"SET_HALLCONF HC_12")
        setParameter(self.serial_port, b"SET_FILTER FILTER_0")
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_0")
        data = readStatus(self.serial_port)
        assert data["oversampling"] == "OSR_3"

    def test_when_hc_equals_12_and_filter_equals_0_then_oversampling_cant_be_set_to_1(
        self,
    ):
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_3")
        setParameter(self.serial_port, b"SET_HALLCONF HC_12")
        setParameter(self.serial_port, b"SET_FILTER FILTER_0")
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_1")
        data = readStatus(self.serial_port)
        assert data["oversampling"] == "OSR_3"

    def test_when_hc_equals_0_and_oversampling_equals_0_then_filter_can_be_set_to_0(
        self,
    ):
        setParameter(self.serial_port, b"SET_FILTER FILTER_7")
        setParameter(self.serial_port, b"SET_HALLCONF HC_0")
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_0")
        setParameter(self.serial_port, b"SET_FILTER FILTER_0")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_0"

    def test_when_hc_equals_0_and_oversampling_equals_0_then_filter_can_be_set_to_1(
        self,
    ):
        setParameter(self.serial_port, b"SET_FILTER FILTER_7")
        setParameter(self.serial_port, b"SET_HALLCONF HC_0")
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_0")
        setParameter(self.serial_port, b"SET_FILTER FILTER_1")
        data = readStatus(self.serial_port)
        assert data["filter"] == "FILTER_1"

    def test_when_hc_equals_0_and_filter_equals_0_then_oversampling_can_be_set_to_0(
        self,
    ):
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_3")
        setParameter(self.serial_port, b"SET_HALLCONF HC_0")
        setParameter(self.serial_port, b"SET_FILTER FILTER_0")
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_0")
        data = readStatus(self.serial_port)
        assert data["oversampling"] == "OSR_0"

    def test_when_hc_equals_0_and_filter_equals_0_then_oversampling_can_be_set_to_1(
        self,
    ):
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_3")
        setParameter(self.serial_port, b"SET_HALLCONF HC_0")
        setParameter(self.serial_port, b"SET_FILTER FILTER_0")
        setParameter(self.serial_port, b"SET_OVERSAMPLING OSR_1")
        data = readStatus(self.serial_port)
        assert data["oversampling"] == "OSR_1"


class TestAvailableModes:
    serial_port = serial.Serial()

    @classmethod
    def setup_class(cls):
        cls.serial_port.baudrate = 115200
        cls.serial_port.port = "/dev/ttyACM0"
        cls.serial_port.open()

    @classmethod
    def teardown_class(cls):
        cls.serial_port.close()

    def test_when_set_mode_dynamic_then_measurement(self):
        setParameter(self.serial_port, b"SET_MODE MODE_DYNAMIC")
        measurement = readMeasurement(self.serial_port)
        assert measurement is not None

    def test_when_set_mode_always_on_then_measurement(self):
        setParameter(self.serial_port, b"SET_MODE MODE_ALWAYS_ON")
        measurement = readMeasurement(self.serial_port)
        assert measurement is not None


def readStatus(serial_port):
    serial_port.write(b"STATUS")
    text = ""
    for i in range(9):
        text += str(serial_port.readline())
    serial_port.read()  # \r character
    text = "".join(text)
    text = text.replace("b'", "")
    text = text.replace("'", "")
    text = text.replace("\\n", "\n")
    text = text.replace("\\r", "\r")
    pattern = "VERSION (?P<version>[0-9,.]+) BUILD DATE: (?P<buildday>[ ,A-Z,0-9,a-z]+)\n\rSTATUS\n\r(?P<status>[A-Z]+)\n\rMODE: (?P<mode>[A-Z,_]+)\n\rGAIN: (?P<gain>[A-Z,0-9,_]+)\n\rRESOLUTION: (?P<resolution>[A-Z,0-9,_]+)\n\rFILTER: (?P<filter>[A-Z,0-9,_]+)\n\rOVERSAMPLING: (?P<oversampling>[A-Z,0-9,_]+)\n\rHALLCONF: (?P<hallconfig>[A-Z,0-9,_]+)\n"
    result = re.match(pattern, text)
    return result


def setParameter(serial_port, parameter):
    serial_port.write(parameter)
    response = serial_port.readline()
    serial_port.read()  # \r character


def readMeasurement(serial_port):
    serial_port.write(b"READ_SINGLE")
    text = ""
    text += str(serial_port.readline())
    serial_port.read()  # \r character
    text = text.replace("b'", "")
    text = text.replace("'", "")
    pattern = "X: (?P<x>[0-9,.,-]+) Y: (?P<y>[0-9,.,-]+) Z: (?P<z>[0-9,.,-]+)"
    result = re.match(pattern, text)
    return result
