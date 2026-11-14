class Combatant:
    def __init__(self, x, y, max_health):
        self.x = float(x)
        self.y = float(y)
        self.max_health = max_health
        self.health = max_health
        self.facing = 1
        self.blocking = False

    @property
    def alive(self):
        return self.health > 0

    def take_damage(self, amount, attacker_x):
        if not self.alive:
            return 0 

        damage = amount
        attacker_is_in_front = (attacker_x - self.x) * self.facing >= 0
        if self.blocking and attacker_is_in_front:
            damage = max(1, round(amount * 0.2))

        self.health = max(0, self.health - damage)
        return damage
