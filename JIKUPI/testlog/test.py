import BASEUtile.BusinessUtil as BusinessUtil

if __name__ == '__main__':
    _charge_state_list = ["未充电", "充电准备", "关机充电", "开机充电", "充电完成", "故障"]
    _battery_state_list = ["未知", "检测到电池", "未检测到电池"]
    _uav_state_list = ["未知", "无人机开机", "无人机关机"]
    result = "010406005144e8000a899c"
    sub_result = BusinessUtil.hex_str_to_bin_str(result[6:10])
    charge_state = BusinessUtil.bin_str_to_int(sub_result[4:])  # 充电状态
    battery_state = BusinessUtil.bin_str_to_int(sub_result[2:4])  # 电池状态
    uav_state = BusinessUtil.bin_str_to_int(sub_result[0:2])  # 开关机状态
    print(result[6:10])
    print(sub_result)
    print(sub_result[4:])
    print(charge_state)
    print(sub_result[2:4])
    print(battery_state)
    print(sub_result[0:2])
    print(uav_state)

    print(
        f"[JCCServerV5.Check]执行状态命令-充电状态:{charge_state},{_charge_state_list[charge_state]}."
        f"电池状态:{battery_state},{_battery_state_list[battery_state]}.开关机状态:{uav_state},{_uav_state_list[uav_state]}")
