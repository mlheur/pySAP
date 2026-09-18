from . import ControlLine

if __name__ == "__main__":
    n = 6
    lines = [None] * n
    for i in range(n):
        lines[i] = ControlLine(position=i,inverted=(i%3==0))
        lines[i].setTruth(False)

    for line in lines:
        print(line)
    print()

    word = 0b111111

    for line in lines:
        line.update(word)

    for line in lines:
        print(line)
    print()
