from PySide2 import QtCore



def greet(name: str, name_list: list):
    print("hello, " + name)
    print(name_list)

class Communicate(QtCore.QObject):
    speak = QtCore.Signal(str, list)




if __name__ == '__main__':
    o = QtCore.QObject()


    someone = Communicate()


    someone.speak.connect(greet)

    someone.speak.emit("lemon", ['a', 'b'])
