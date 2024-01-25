from random import randint
import math 

def filtrer(critere, liste, l = []): # Fonction récursive qui permet de filtrer une liste
    if len(liste) == 0:
        return l
    else:
        if critere(liste[0]):
            return filtrer(critere, liste[1:], l+[liste[0]])
        else:
            return filtrer(critere, liste[1:], l)

class Poisson: # Classe des poissons
    def __init__(self, vitesse, vision, x, y):
        self.vitesse = vitesse
        self.vision = vision
        self.x = x
        self.y = y
        self.vx = vitesse
        self.vy = vitesse
        self.vie = 100
        self.age = 0
        self.directionAleatoire()
    def __str__(self):
        return f"Poisson de vitesse {self.vitesse}, vision: {self.vision} | X: {self.x} Y: {self.y}"
    def proche(self, liste):
        """
            self: Poisson, liste: List
            Retourne une liste d'éléments proches du poisson 
        """
        return filter(lambda n: math.sqrt((self.x-n.x)**2+(self.y-n.y)**2) <= self.vision*10, liste)
    def estSur(self, liste):
        """
            self: Poisson, liste: List
            retourne l'élémént de la liste (si il y en a) sur le poisson (False sinon) 
        """
        nrtr = self.proche(liste)
        for n in nrtr:
            if math.sqrt((self.x-n.x)**2+(self.y-n.y)**2) <= self.vision:
                return n
        return False
    def reproduction(self, poisson, oeufs):
        """
            self: Poisson, poisson: Poisson, Oeufs: List<Oeuf>
            Effectue une reproduction entre self et poisson, réinitialise le cooldown des deux, rajoute un oeuf dans Oeufs
        """
        oeufs.append(Oeuf((self.x+poisson.x)/2, (self.y+poisson.y)/2, self, poisson)) # On crée un oeuf entre les deux poissons
        self.age = 0
        poisson.age = 0
        self.directionAleatoire()
        poisson.directionAleatoire()
    def directionAleatoire(self):
        """
            self: Poisson
            Rend la position de self aléatoire (soit droite soit gauche + soit haut soit bas)
        """
        self.vx = randint(-200,200)/100*self.vitesse
        self.vy = randint(-200,200)/100*self.vitesse
    def tick(self, L, H, poissons):
        """
            self: Poisson, L: Number > 0, H: Number > 0, poissons: List<Poisson>
        """
        self.x += self.vx
        self.y += self.vy
        # On fait vieillir le poisson
        self.age += 0.02
        self.vie -= 0.1
        # On vérifie si le poisson est mort
        if self.vie <= 0:
            if self in poissons:
                poissons.remove(self)
        # Rebond sur les bords
        if self.x >= L or self.x <= 0:
            self.vx = -self.vx
        if self.y <= 0 or self.y >= H:
            self.vy = -self.vy
        # Changement de direction aléatoire
        if randint(0,200) == 0:
            self.directionAleatoire()
            
class Nourriture:
    def __init__(self, x, y, donvie):
        self.x = x
        self.y = y
        self.donvie = donvie
    def __str__(self):
        return f"Nourriture +{self.donvie} | X: {self.x} Y: {self.y}"
    
class Oeuf:
    def __init__(self, x, y, p1, p2):
        self.x = x
        self.y = y
        self.p1 = p1
        self.p2 = p2
        self.eclosion = 0
    def __str__(self):
        return f"Oeuf | X: {self.x} Y: {self.y}"
    
    def eclore(self, poissons, oeufs):
        """
            self: Oeuf, poissons: List<Poisson>, oeufs: List<Oeufs>
            Eclore l'oeuf si le % d'éclosion est >= 100, ne rien faire sinon
            Puis, faire apparaître un poisson avec une variation génétique de vitesse et de vision (simulation de la vie réelle)
        """
        if self.eclosion < 100:
            return
        
        oeufs.remove(self)
        poissons.append(Poisson((self.p1.vitesse+self.p2.vitesse)/2+randint(-100,500)/1000, (self.p1.vision+self.p2.vision)/2+randint(-100,500)/1000, self.x, self.y))
        
