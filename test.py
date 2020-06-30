from threading import Timer

import schedule

import util

class MainWindow:
    def show_name(self, str):
        print(str)

    def polling(self):
        self.show_name(util.get_time())
        timer = Timer(1, self.polling)
        timer.start()



if __name__ == '__main__':

    main_window = MainWindow()
    
    timer = Timer(0, polling)
    timer.start()

