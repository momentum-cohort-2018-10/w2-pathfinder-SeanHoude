from PIL import Image
import operator
import sys

sys.setrecursionlimit(1202)

class Imager:
    '''
    Accepts data and scale to create an image from the data
    '''
    def __init__(self, data_file, image_name, height, width):
        self.data_file = data_file
        self.image_name = image_name
        self.height = height
        self.width = width
        self.pillow_image = None

        # open and read data file
        with open(self.data_file, 'r', buffering=20000000) as f:
            file = [line.strip('\n').split() for line in f]

        # find min and max values in data in order to transform data to fit in 0-255
        flat_list = [int(y) for x in file for y in x]
        high = max(flat_list)
        low = min(flat_list)
        # create a 2d list with elevation data 
        self.elevation = [[int((int(y) - low) / (high - low) * 255) for y in x] for x in file]

    def print_map(self, list):
        '''
        takes elevation data and plots them to make a topographical map
        '''
        self.pillow_image = Image.new("RGB", (self.height, self.width), "green")
        for y, row in enumerate(list):
            for x, value, in enumerate(row):
                self.pillow_image.putpixel((x, y), (value, value, value))
        self.pillow_image.save(self.image_name)

    def print_path(self, path):
        '''
        Takes a list of tuples with coordinates and plots a red line at each coordinate to mark a path
        '''
        for tuple in path:
            self.pillow_image.putpixel((tuple[0], tuple[1]), (255, 0, 0))
        self.pillow_image.save(self.image_name)

class PathFinder:
    '''
    Takes a start position and determines the path of least resistance
    '''
    def __init__(self, imager_instance, place):
        self.imager = imager_instance
        self.place = place
        self.path = []

    # def instantiate_imager(self, data_file, pillow_image, height, width):
    #     self.imager = Imager(data_file, pillow_image, image_name, height, width)
        
    def get_choices(self, place):
        '''
        Determines possible moves depending on previous position to prevent leaving the bounds of the map
        '''
        (x, y) = self.place
        choices = {}
        if y == self.imager.width - 1:
            choices['straight'] = (self.imager.elevation[y][x + 1])
            choices['down'] = (self.imager.elevation[y - 1][x + 1])
        elif y == 0:
            choices['up'] = (self.imager.elevation[y + 1][x + 1])
            choices['straight'] = (self.imager.elevation[y][x + 1])
        else:
            choices['up'] = (self.imager.elevation[y + 1][x + 1])
            choices['straight'] = (self.imager.elevation[y][x + 1])
            choices['down'] = (self.imager.elevation[y - 1][x + 1])
        return choices

    def choose_path(self):
        (x, y) = self.place
        if x < self.imager.width - 2:
            choices = self.get_choices(self.place)
            difference = {}
            for k, v in choices.items():
                difference[k] = abs(v - self.imager.elevation[y][x])     
            if difference['up'] == difference['straight']:
                difference['up'] = 0
            if difference['down'] == difference['straight']:
                difference['down'] = 0
            best_path = max(difference.items(), key=operator.itemgetter(1))[0]
            if best_path == 'up':
                self.place = ((x + 1), (y + 1))
            elif best_path == 'down':
                self.place = ((x + 1), (y - 1))
            else:
                self.place = ((x + 1), (y))
            self.path.append((x, y))
            self.choose_path()

small = Imager("elevation_small.txt", "elevation_map.png", 600, 600)
small.print_map(small.elevation)
midway_small = (0, 300)
pathfinder_small = PathFinder(small, midway_small)
pathfinder_small.choose_path()
small.print_path(pathfinder_small.path)

large = Imager("elevation_large.txt", "elevation_map_large.png", 1201, 1201)
large.print_map(large.elevation)
midway_large = (0, 600)
pathfinder_large = PathFinder(large, midway_large)
pathfinder_large.choose_path()
large.print_path(pathfinder_large.path)
