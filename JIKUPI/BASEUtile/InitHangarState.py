import BASEUtile.HangarState as HangarState
import BASEUtile.Config as Config
import BASEUtile.OperateUtil as OperateUtil
import BASEUtile.BusinessConstant as BusinessConstant


class InitHangarState:
    """
    初始化机库相关信息
    """

    def __init__(self, logger):
        self._logger = logger

    def init_hangar(self):
        """
        初始化机库状态
        """
        # 初始化升降台状态
        self._init_updown_lift_state()
        # 初始化旋转台状态
        self._init_turn_lift_state()
        # 初始化机库版本
        self._init_hangar_version()
        # 初始化门状态
        self._init_hangar_door_state()
        # 初始化推杆状态
        self._init_hangar_bar_state()

    def _init_updown_lift_state(self):
        """
        初始化升降台状态
        """
        self._logger.get_log().info(f"[InitHangar._init_updown_lift_state]初始化升降台状态-开始")
        result = OperateUtil.operate_hangar("730000")
        if result == "9730":
            self._logger.get_log().info(
                f"[InitHangar._init_updown_lift_state]初始化升降台状态-结束,初始化成功,状态为:{HangarState.get_updown_lift_state()}")
        else:
            updown_lift_state = Config.get_updown_lift_state()
            HangarState.set_updown_lift_state(updown_lift_state)
            self._logger.get_log().info(f"[InitHangar._init_updown_lift_state]初始化升降台状态-结束,初始化失败,从配置文件中获取状态为:{updown_lift_state}")

    def _init_turn_lift_state(self):
        """
        初始化旋转台状态
        """
        self._logger.get_log().info(f"[InitHangar._init_turn_lift_state]初始化旋转台状态-开始")
        result = OperateUtil.operate_hangar("830000")
        if result == "9830":
            self._logger.get_log().info(f"[InitHangar._init_turn_lift_state]初始化旋转台状态-结束,初始化成功,状态为:{HangarState.get_turn_lift_state()}")
        else:
            turn_lift_state = Config.get_turn_lift_state()
            HangarState.set_turn_lift_state(turn_lift_state)
            self._logger.get_log().info(f"[InitHangar._init_turn_lift_state]串口初始化旋转台状态-结束,初始化失败,从配置文件中获取状态为:{turn_lift_state}")

    def _init_hangar_version(self):
        """
        初始化机库版本
        """
        hangar_version = Config.get_hangar_version()
        HangarState.set_hangar_version(hangar_version)
        self._logger.get_log().info(f"[InitHangar._init_hangar_version]初始化机库版本为:{hangar_version}")

    def _init_hangar_door_state(self):
        """
        初始化机库门状态
        """
        self._logger.get_log().info(f"[InitHangar._init_hangar_door_state]初始化门状态-开始")
        result = OperateUtil.operate_hangar("170000")
        if result == "9170":
            self._logger.get_log().info(f"[InitHangar._init_hangar_door_state]初始化门状态-结束,初始化成功,状态为:{HangarState.get_hangar_door_state()}")
        else:
            hangar_door_state = Config.get_hangar_door_state()
            HangarState.set_hangar_door_state(hangar_door_state)
            self._logger.get_log().info(f"[InitHangar._init_hangar_door_state]串口初始化门状态-结束,初始化失败,从配置文件中获取状态为:{hangar_door_state}")

    def _init_hangar_bar_state(self):
        """
        初始化推杆状态
        """
        self._logger.get_log().info(f"[InitHangar._init_hangar_bar_state]初始化推杆状态-开始")
        result = OperateUtil.operate_hangar("2g0000")
        if result == "92g0":
            self._logger.get_log().info(f"[InitHangar._init_hangar_bar_state]初始化推杆状态-结束,初始化成功,状态为:{HangarState.get_hangar_bar_state()}")
        else:
            hangar_bar_state = Config.get_hangar_bar_state()
            HangarState.set_hangar_bar_state(hangar_bar_state)
            HangarState.set_hangar_lr_bar_state(hangar_bar_state)
            HangarState.set_hangar_td_bar_state(hangar_bar_state)
            self._logger.get_log().info(f"[InitHangar._init_hangar_bar_state]串口初始化推杆状态-结束,初始化失败,从配置文件中获取状态为:{hangar_bar_state}")
