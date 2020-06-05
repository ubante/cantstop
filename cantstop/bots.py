from cantstop.all_the_things import Player


class SimpleBot(Player):
    """
    Eventually, this will override the abstract methods in superclass.
    """
    def __init__(self, name):
        super().__init__()
        self.name = name

    def choose_columns(self, state):
        print("SimpleBot, {}, is passing on choosing columns.".format(self.name))

