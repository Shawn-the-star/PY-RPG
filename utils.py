from os import walk
from csv import reader
import pygame

def import_csv_map(path):
    e = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            e.append(list(row))

    return e

def import_folder(path):
    surface = []

    for _,__, image_files in walk(path):
        for image in image_files:
            img_surf = pygame.image.load(path + '/' + image).convert_alpha()
            surface.append(img_surf)

    return surface
