import BASEUtile.Config as Config
from Lift.UpdownLift import UpdownLift
from Lift.UpdownLiftV2 import UpdownLiftV2
import BASEUtile.BusinessConstant as BusinessConstant


class UpdownLiftCommon:
    def __init__(self, logger):
        self._logger = logger
        if Config.get_updown_lift_version() == "V2.0":
            self._updownLift = UpdownLiftV2(logger)
        else:
            self._updownLift = UpdownLift(logger)

    def up_lift(self):
        result = self._updownLift.up_lift()
        return result

    def down_lift(self):
        result = self._updownLift.down_lift()
        return result

    def reset_lift(self):
        result = self._updownLift.reset_lift()
        return result

    def get_lift_state(self):
        if Config.get_updown_lift_version() == "V2.0":
            result = self._updownLift.get_lift_state()
            return result
        else:
            self._logger.get_log().info(f"[UpdownLiftCommon.get_lift_state]获取升降台状态-异常,该版本无法获取状态,现在配置版本为:{Config.get_updown_lift_version()}")
            return BusinessConstant.ERROR
