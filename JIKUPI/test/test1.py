from test import test

t11 = None


def fun2(t1):
    global t11
    if t1 is not None:
        print("test1")
    print(f"fun2:{t1.fun1()}")


if __name__ == '__main__':
    # global t11
    t11 = test()
    # t1.fun1()
    fun2(t11)
