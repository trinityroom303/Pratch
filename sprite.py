import pygame
import math

class Sprite():
    def __init__(self, image_path, base_x = 0, base_y = 0):
        self.image = pygame.image.load(image_path)
        self.width = None
        self.lenght = None
        self.angle = 0 # Degrees
        self.x = base_x
        self.y = base_y
        self.touching_mouse = False
        self.touching_edge = False

    def move_sprite(self, pixels):
        self.x += pixels * math.cos(self.angle)
        self.y += pixels * - math.sin(self.angle)

    def turn(self, direction, degrees):
        if direction == "left":
            self.angle -= degrees
        else:
            self.angle += degrees
    
    # Percentage < 100 -> Scale down
    # Percentage > 100 -> Scale up
    def scale(self, percetage):
        percetage /= 100
        self.width *= percetage
        self.lenght *= percetage

    def go_to(self, goal_x , goal_y):
        self.x = goal_x
        self.y = goal_y

    def display(self, screen):
        screen.blit(self.image, (self.x, self.y))
        pygame.transform.rotate(screen, self.angle)
        if pygame.mouse.get_pos() == (self.x , self.y):
            self.touching_mouse = True
        

# Getters
    def get_pos(self):
        return self.x,self.y
    def get_angle(self):
        return self.angle