import random, string
def TagGenerator():
    x = ''.join(random.choices(string.ascii_letters + string.digits, k=10)).lower()
    return x
