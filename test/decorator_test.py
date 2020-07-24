


def Slot(func, x:int = 5, y: str = "hello"):
    print("x=%d" % x)
    print("y=%s" % y)
    return "hello"

@Slot
def show_name(name: str):
    print(name)


if __name__ == '__main__':
    print(show_name())