def open_bar_1(bar_move_style="ALL"):
    """
    推杆打开
    """
    try:
        print(f"[JKBarServer.open_bar]推杆打开-开始")
        open_command = "2f13002364"
        close_command = "2e13002364"
        # BusinessUtil.open_serial(self._com_serial, self._logger)
        if bar_move_style == "TDF":
            command = open_command[:2] + close_command[2:6] + "2000"
        elif bar_move_style == "LRF":
            command = open_command[:2] + "1000" + close_command[6:]
        else:
            command = open_command
        # result = BusinessUtil.execute_command(command + "\r\n", self._com_serial, self._logger, is_hex=False,
        #                                       byte_size=4)
        print(f"[JKBarServer.open_bar]推杆打开-结束,返回值为{command}")
        # print(f"[JKBarServer.open_bar]推杆打开-结束,返回值为{result}")
        # return result
    except Exception as ex:
        print(f"[JKBarServer.close_bar]推杆夹紧-异常,异常信息:{str(ex)}")


class test:
    def __init__(self):
        pass

    def fun1(self):
        print("fun1")


if __name__ == '__main__':
    open_bar_1()
