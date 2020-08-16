import sys
import time


class showProgress():
    """
    Class to show progress in long-running tasks
    
    from showProgress import showProgress
    dot = showProgress()
    dot.show()  # print a single character to show progress
    dot.end()  # End the sequence, print newline

    Default character is period(.), you can change the character:
        dot = showProgress(dotchar="#")
    """
    

    def __init__(self, dotchar="."):
        """ Set characters to use for showing progress"""
        self.dotchar = dotchar

    def show(self):
        """ Display a single dot """
        sys.stdout.write(self.dotchar)
        sys.stdout.flush()
        return None

    def end(self):
        """ End the sequence of dots """
        print("")
        sys.stdout.flush()
        return None

if __name__ == "__main__":
    print('Testing: ', sys.argv[0])

    dot = showProgress()
    for n in range(50):
        dot.show()
        time.sleep(0.3)
    dot.end()

    print('Testing with different character')
    dash = showProgress(dotchar='#')
    for n in range(50):
        dash.show()
        time.sleep(0.2)
    dash.end()

    print('Changing character midway')
    hash = showProgress(dotchar="#")
    for n in range(50):
        hash.show()
        if n>27:
            hash.dotchar="@"
        time.sleep(0.1)
    hash.end()
    print('Congratulations')



