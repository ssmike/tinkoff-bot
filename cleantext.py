import sys
inp = sys.argv[1]

chars = u'.,:;?!()<>«»–-\n' + u'"' + u"'"

def clean(line):
    acc = ""
    for c in line:
        if c == '$':
            acc += ' доллар '
        elif c not in chars:
            acc += c
        else:
            acc += " "
    return acc

if __name__ == "__main__":
    with open(inp) as inpfile:
        for line in inpfile:
            if line.startswith('+'):
                continue
            print(clean(line))

