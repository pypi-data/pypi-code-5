
def smatch(string, sregex):
    sregexes = sregex.split("|")
    if len(sregexes) == 1:
        return sregex == "*" or sregex == string
    for sr in sregexes:
        if smatch(string, sr):
            return True
    return False
