import secrets


class Random:

    characters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t",
                  "u", "v", "w", "x", "y", "z",
                  "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                  "U", "V", "W", "X", "Y", "Z",
                  "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    def __init__(self):
        self.random = secrets.SystemRandom()

    def random_string(self, minimum: int = 15, maximum: int = 20) -> str:
        length = self.random.randint(minimum, maximum)
        return "".join(self.random.choice(self.characters) for _ in range(length))
