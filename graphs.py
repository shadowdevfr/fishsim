# Module de graphiques pour stats de la simulation
import matplotlib.pyplot as plt

def afficherGraphique(evolution):
    plt.title("Évolution de la vision et de la vitesse moyenne des poissons en fonction du temps")
    plt.plot(evolution["temps"], evolution["vitesses"])
    plt.plot(evolution["temps"], evolution["visions"])
    
    plt.xlabel("Temps (ms)")
    plt.ylabel("Vitesse (bleu) et vision (orange)")
    
    plt.show()