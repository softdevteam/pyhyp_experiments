import sys

H1 = 150

def mandel_py(n):
    lines = []

    w1 = n
    h1 = H1
    recen = -0.45
    imcen = 0.0
    r = 0.7
    s = 0
    rec = 0
    imc = 0
    re = 0
    im = 0
    re2 = 0
    im2 = 0
    x = 0
    y = 0
    w2 = 0
    h2 = 0
    color = 0
    s = 2 * r / w1
    w2 = 40
    h2 = 12

    for y in xrange(w1 + 1):
        line = []
        imc = s * (y - h2) + imcen
        for x in xrange(h1 + 1):
            rec = s * (x - w2) + recen
            re = rec
            im = imc
            color = 1000
            re2 = re * re
            im2 = im * im
            while re2 + im2 < 1000000 and color > 0:
                im = re * im * 2 + imc
                re = re2 - im2 + rec
                re2 = re * re
                im2 = im * im
                color = color - 1

            if color == 0:
                line.append("_")
            else:
                line.append("#")
        lines.append("".join(line))
    out = "\n".join(lines) + "\n"
    return out


def run_iter(n):
    out = mandel_py(n)
    assert len(out) == (H1 + 2) * (n + 1)
    #print(out)

run_iter(50)
