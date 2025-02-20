import pygame
from sprite import Sprite

WIDTH = 500
HEIGHT = 500
class Game:
    def __init__(self):
        pygame.init()
        # Display surface -> Game attribute
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Pratch")
        self.running = True
        
        # Lists backgrounds / sprites 
        self.backgrounds = [ f"background{i}.jpg" for i in range(1,5) ]
        self.sprites = [ Sprite(f"character{i}.png") for i in range(1,5)]
        
        # Indexes for the lists above
        self.current_sprite = 0
        self.current_background = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def main_loop(self):
        while self.running:
            self.handle_events()
            self.sprites[self.current_sprite].display(self.screen)
            pygame.display.update()

pratch = Game()

def hide_cursor():
        pygame.mouse.set_visible(False)
    
def show_cursor():
    pygame.mouse.set_visible(True)

def move(px, game = pratch):
    game.sprites[game.current_sprite].move_sprite(px)

"""
Je sais c'est un peu répétitif mais je trouve que c'est 
une façon d'être completement 'commme scratch' (voir test)
Je suis 100% ouverte a un meilleur systeme ! :)
"""

def start():
    pratch.main_loop()
    