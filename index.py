import pygame, sys
import math
from pygame.locals import QUIT
from random import randint
from classes import *
import graphs
# Javascript c'est mieux que python

print("===== Chargement des images =====")
pygame.init()

tailleEcran = pygame.display.get_desktop_sizes()[0]
# Paramètres
H = tailleEcran[1] # Hauteur de l'écran
L = tailleEcran[0] # Largeur de l'écran
fps = 60 # Nombre de fps
NB_DEBUT = 30 # Nombre de départ de poissons | Bonne valeur: 50
VIE_MINI_REPRO = 10 # Vie minimum pour se reproduire

# Initialisation de pygame
screen = pygame.display.set_mode((L, H), vsync=1)
pygame.display.set_caption('Simulation de poissons')
font = pygame.font.SysFont(None, 18)
bfont = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

# Initialisation des variables nécéssaires
poissons = []
nourriture = []
oeufs = []

vitesses = []
visions = []
showHUD = True

def genPoisson():
    pb = Poisson(randint(100,800)/500, randint(0,800)/100, randint(0,L), randint(0,H))
    poissons.append(pb)

def genNourriture():
    nt = Nourriture(randint(0,L), randint(0,H), randint(1,10))
    nourriture.append(nt)

for i in range(NB_DEBUT):
    genPoisson()

simulations = []
stats = {"vitesse": 0, "vision": 0, "poissons": 0, "nourriture": 0, "oeufs": 0, "temps": 0}
maxNourriture = 500
# Chargement des images
imgPoissonG = pygame.image.load('poisson.png').convert_alpha()
imgPoissonR = pygame.transform.flip(imgPoissonG, True, False)
imgFond = pygame.image.load("fond.jpg").convert()
vitesseMoyenneDebut = 0
visionMoyenneDebut = 0

evolution = {"vitesses": [], "visions": [], "temps": []}

while 1:
    stats["temps"] += clock.get_time()
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    # Statistiques
    if len(poissons) > 0:
        vitesse_moyenne = round(sum([p.vitesse for p in poissons])/len(poissons), 2)
        vision_moyenne = round(sum([p.vision for p in poissons])/len(poissons), 2)
    if len(poissons) > stats["poissons"]:
        stats["poissons"] = len(poissons)
    if len(nourriture) > stats["nourriture"]:
        stats["nourriture"] = len(nourriture)
    if len(oeufs) > stats["oeufs"]:
        stats["oeufs"] = len(oeufs)
    if vision_moyenne > stats["vision"]:
        stats["vision"] = vision_moyenne
        if vitesseMoyenneDebut == 0:
            visionMoyenneDebut = vision_moyenne
    if vitesse_moyenne > stats["vitesse"]:
        stats["vitesse"] = vitesse_moyenne
        if vitesseMoyenneDebut == 0:
            vitesseMoyenneDebut = vitesse_moyenne
    if stats["temps"] % 1000 == 0:
        evolution["vitesses"].append(vitesse_moyenne)
        evolution["visions"].append(vision_moyenne)
        evolution["temps"].append(stats["temps"])
    
    # Fond
    screen.blit(imgFond, (0,0))
    # Controles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_F3]:
        showHUD = not showHUD
    if keys[pygame.K_n]:
        genPoisson()
    if keys[pygame.K_KP_PLUS]:
        fps = 1000
    elif fps > 60: fps = 60
    if keys[pygame.K_d]:
        if len(poissons)>0:
            poissons.remove(poissons[randint(0,len(poissons)-1)])
    souris = pygame.mouse.get_pressed()
    if souris[0]: # Clic gauche
        pos = pygame.mouse.get_pos()
        if pos == (0,0):
            graphs.afficherGraphique(evolution)
        poissonsProches = filter(lambda p: math.sqrt((p.x-pos[0])**2 + (p.y-pos[1])**2) <= 20, poissons)

        for pp in poissonsProches:
            pygame.draw.rect(screen, "white", pygame.Rect(pp.x-10, pp.y-10, 20, 20), 1)
            pygame.draw.rect(screen, "black", pygame.Rect(pp.x-5, pp.y+20, 150, 100))
            screen.blit(font.render(f"Vie: {round(pp.vie,2)}", True, "white"), (pp.x+5,pp.y+40))
            screen.blit(font.render(f"Vitesse: {round(pp.vitesse,2)}", True, "white"), (pp.x+5,pp.y+60))
            screen.blit(font.render(f"Vision: {round(pp.vision,2)}", True, "white"), (pp.x+5,pp.y+80))
    
    if souris[2]: # Clic droit
        pos = pygame.mouse.get_pos()
        nourriture.append(Nourriture(pos[0], pos[1], randint(1,10)))
        screen.blit(font.render(str((pos[0], pos[1])), True, "white"), (pos[0]+5,pos[1]+40))
        
    # Rendu poissons
    for p in poissons:
        # Tick du poisson (vieillissement & déplacement)
        p.tick(L, H, poissons)
        
        # Reproduction
        for p2 in p.proche(poissons):
            if math.sqrt((p.x-p2.x)**2 + (p.y-p2.y)**2) < p.vision*10 and p != p2 and p.age > 5 and p2.age > 5 and p.vie >= VIE_MINI_REPRO and p2.vie >= VIE_MINI_REPRO and len(oeufs) < 100 and len(poissons) < 100: # Si la distance entre la vision du poisson et la vision du poisson 2 est inférieure à la vision du poisson
                p.reproduction(p2, oeufs)
        
        # Nourriture
        n = p.estSur(nourriture) # Retourne nourriture si le poisson est sur la nourriture, False sinon
        if type(n) == Nourriture: # Le poisson passe par la nourriture
            if n in nourriture:
                nourriture.remove(n)
            p.vie += n.donvie
            p.directionAleatoire()
        for n in p.proche(nourriture): # Pour chaque nourriture proche
            # Le poisson va vers la nourriture
            pygame.draw.line(screen, "white", (p.x, p.y), (n.x, n.y))
            p.vx = (n.x-p.x)/(20-p.vitesse)
            p.vy = (n.y-p.y)/(20-p.vitesse)
        
        pygame.draw.circle(screen, "green" if p.age > 5 and p.vie >= VIE_MINI_REPRO else "red", pygame.Vector2(p.x,p.y), p.vision*10, 1)
        
        screen.blit(imgPoissonG if p.vx < 0 else imgPoissonR, (p.x-10,p.y-10))
        screen.blit(font.render(str(round(p.vie)), True, "white"), (p.x-5,p.y+10))
    
    # Rendu nourriture
    for n in nourriture:
        pygame.draw.circle(screen, "orange", pygame.Vector2(n.x,n.y), n.donvie/2)
        pygame.display.update
                
    for o in oeufs:
        pygame.draw.circle(screen, "violet", pygame.Vector2(o.x,o.y), 5)
        screen.blit(font.render(f"{math.floor(o.eclosion)}%", True, "white"), (o.x,o.y))
        o.eclosion += 0.5
        pygame.draw.line(screen, "black", (o.x, o.y), (o.p1.x, o.p1.y))
        pygame.draw.line(screen, "black", (o.x, o.y), (o.p2.x, o.p2.y))
        if o.eclosion >= 100:
            o.eclore(poissons, oeufs)
        
    if randint(0,10) == 1 and len(nourriture)<maxNourriture:
        genNourriture()
    maxNourriture = 500-len(poissons)*4
    
    if len(poissons) < 2 and len(oeufs) < 2:
        simulations.append(stats)
        nourriture = []
        poissons = []
        evolution = {"vitesses": [], "visions": [], "temps": []}
        oeufs = []
        stats = {"vitesse": 0, "vision": 0, "poissons": 0, "nourriture": 0, "oeufs": 0, "temps": 0}
        for i in range(NB_DEBUT):
            genPoisson()
    elif showHUD:
        # HUD (infos sur la simulation)
        screen.blit(bfont.render(f"{round(clock.get_fps(), 2)}/{fps} fps", True, "white"), (L-200, 20))
        screen.blit(bfont.render(f"Temps écoulé: {stats['temps']}ms", True, "white"), (L-200, 40))
        screen.blit(bfont.render(f"Nb poissons: {len(poissons)}", True, "white"), (20, 20))
        screen.blit(bfont.render(f"Nb nourriture: {len(nourriture)}/{maxNourriture}", True, "white"), (20, 40))
        screen.blit(bfont.render(f"Nb oeufs: {len(oeufs)}", True, "white"), (20, 60))
        screen.blit(bfont.render(f"Vitesse moyenne: {vitesse_moyenne} | Début: {vitesseMoyenneDebut} | Max: {stats['vitesse']}", True, "white"), (20, 80))
        screen.blit(bfont.render(f"Vision moyenne: {vision_moyenne} | Début: {visionMoyenneDebut} | Max: {stats['vision']}", True, "white"), (20, 100))
        
        if len(simulations) > 0:
            screen.blit(font.render("====== Simulations ======", True, "white"), (20, 140))
            sh = 140
            for s in simulations:
                sh += 20
                screen.blit(font.render(f'#{simulations.index(s)} - Vitesse: {s["vitesse"]} | Vision: {s["vision"]} | Poissons: {s["poissons"]} | Nourriture: {s["nourriture"]} | Oeufs: {s["oeufs"]} | Temps: {s["temps"]}ms', True, "white"), (20, sh))
    
    clock.tick(fps) # Limitation du nombre de fps pour controler la vitesse de la simulation
    pygame.display.update()
    
