import BASEUtile.Config as Config
from AirCondition.AirConditionComputer import AirConditionComputer
from AirCondition.AirConditionComputerV2 import AirConditionComputerV2


class AirConditionComputerCommon:
    def __init__(self, logger):
        self._logger = logger
        if Config.get_air_condition_computer_version() == "V2.0":
            self._airConditionComputer = AirConditionComputerV2(logger)
        else:
            self._airConditionComputer = AirConditionComputer(logger)

    def openAircondition(self):
        """
        打开空调
        """
        result = self._airConditionComputer.openAircondition()
        return result

    def closeAircondition(self):
        """
        关闭空调
        """
        result = self._airConditionComputer.closeAircondition()
        return result