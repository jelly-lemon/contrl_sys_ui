import re

if __name__ == '__main__':
    obj = re.match(r"^[0-9]{1,2}$", "12")
    print(obj)
    print(obj.group(0))
