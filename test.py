import main
def test1():
 assert main.sum_two_args(2,2) == 4
def test2():
 assert main.sum_two_args(2.0001,2) == 4
def test3():
 assert main.sum_two_args(3,2) == 5
def test4():
 assert main.sum_two_args("2",2) == 4