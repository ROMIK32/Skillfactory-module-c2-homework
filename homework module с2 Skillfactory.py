from random import randint


class Dot:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __eq__(self, o):
        return self.x == o.x and self.y == o.y


class Ship:
    def __init__(self, ship_bow, lenght, ot):
        self.ship_bow = ship_bow
        self.lenght = lenght
        self.ot = ot
        self.HP = lenght

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.lenght):
            cur_x = self.ship_bow.x
            cur_y = self.ship_bow.y
            if self.ot == 0:
                cur_x += i
            elif self.ot == 1:
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class BoardException(Exception):
    pass


class BoardWrongShipException(BoardException):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "ВЫ БЬЁТЕ ЗА ГОРИЗОНТ!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "ЭТА ЗОНА УЖЕ ПОРАЖЕНА"


class Game_Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["O"] * 6 for _ in range(6)]
        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        pic = ""
        pic += "0 | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            pic += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            pic = pic.replace("■", "O")
        return pic

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)
        for ship in self.ships:
            if d in ship.dots:
                ship.HP -= 1
                self.field[d.x][d.y] = "X"
                if ship.HP == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход врага: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты удара! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа , не буквы ! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        board = Game_Board(size=self.size)
        popip = 0
        lens = [3, 2, 2, 1, 1, 1, 1]
        for l in lens:
            while True:
                popip += 1
                if popip > 1000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("    морской бой    ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Ваши корабли:")
            print(self.us.board)
            print("-" * 20)
            print("Вражеские корабли:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ваш ход!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ход врага!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Победа!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Поражение!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()