from settings import *

class Pathfinder:
    def __init__(self, tmx_map_w, tmx_map_h):
        # flip w and h so that x = rows and y = cols
        self.max_width = tmx_map_w
        self.max_height = tmx_map_h
        self.matrix = [[1] * (tmx_map_h) for _ in range((tmx_map_w))]
        self.path = []
        self.path_checkpoints = []

    def build_matrix(self, obstacles):
        for spr in obstacles:
            x = int(spr.rect.topleft[0] // TILE_SIZE)
            y = int(spr.rect.topleft[1] // TILE_SIZE)
            self.matrix[x][y] = 0

    def empty_path(self):
        self.path = []

    def print_matrix(self, matrix):
        for r in range(len(matrix)):
            for c in range(len(matrix[r])):
                print(f'{str(matrix[r][c]).center(10)}', end= ", ")
            print('-')

    def draw_matrix_rects(self):
        for r in range(len(self.matrix)):
            for c in range(len(self.matrix[r])):
                if (self.matrix[r][c] == 0):
                    pygame.draw.rect(pygame.display.get_surface(), "red", Tile((c * TILE_SIZE, r * TILE_SIZE)).create_rect())

    def bound(self, val, min_val, max_val):
        return max(min(val, max_val), min_val)

    def dijkstra(self, start_coord, end_coord):
        
        # have to resize for index
        start_coord = list([int(z // TILE_SIZE) for z in start_coord])
        end_coord = list([int(z // TILE_SIZE) for z in end_coord])

        start_coord[0] = self.bound(start_coord[0], 0, self.max_width - 1) #self.max_width - 1 if start_coord[0] >= self.max_width else start_coord[0]
        start_coord[1] = self.bound(start_coord[1], 0, self.max_height - 1) #self.max_height - 1 if start_coord[1] >= self.max_height else start_coord[1]

        end_coord[0] = self.bound(end_coord[0], 0, self.max_width - 1)#self.max_width - 1 if end_coord[0] >= self.max_width else end_coord[0]
        end_coord[1] = self.bound(end_coord[1], 0, self.max_height - 1)#self.max_height - 1 if end_coord[1] >= self.max_height else end_coord[1]
        #print(f'{start_coord}, {end_coord}')

        #print(start_coord, " => ", end_coord)
        adj_start_coord = start_coord#[start_coord[1], start_coord[0]] and then flip since x = col and y = row
        adj_end_coord = end_coord#[end_coord[1], end_coord[0]]
        
        rows = len(self.matrix)
        cols = len(self.matrix[0])

        size = rows * cols
        # [4564.08, 877.869], [3605, 595]
        distances = [[float('inf')] * cols for _ in range(rows)]
        distances[adj_start_coord[0]][adj_start_coord[1]] = 0
        visited = [[False] * cols for _ in range(rows)]
        predecessors = [[None] * cols for _ in range(rows)]
        
        directions = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1]]

        for _ in range(size):
            min_distance = float('inf')
            curr = None
            for r in range(rows):
                for c in range(cols):
                    # find next vertex to evaluate, the lowest distance that has not been visited yet. First run will find the starting with value 0
                    if (not visited[r][c] and distances[r][c] < min_distance):
                        min_distance = distances[r][c]
                        curr = [r, c]
                        #print(curr)

            if (curr is None or (curr[0] == adj_end_coord[0] and curr[1] == adj_end_coord[1])):
                # either cannot continue due to no more unvisited edges or found target
                #print(f"Breaking out of loop. Current vertex: {curr}")
                break

            visited[curr[0]][curr[1]] = True

            # evaluate adjacent coordinates
            for dir_r, dir_c in directions:
                new_r = curr[0] + dir_r
                new_c = curr[1] + dir_c
                #print(new_r, ", ", new_c)
                if (new_r < 0 or new_r >= rows or new_c < 0 or new_c >= cols):
                    continue

                if (self.matrix[new_r][new_c] != 0 and not visited[new_r][new_c]):
                    new_dist = distances[curr[0]][curr[1]] + self.matrix[new_r][new_c]  # curr distance to curr node + dist to adj

                    if (new_dist < distances[new_r][new_c]):
                        # update distance in adj node
                        distances[new_r][new_c] = new_dist
                        predecessors[new_r][new_c] = curr

        #self.print_matrix(self.matrix)
        #self.print_matrix(distances)
        #self.print_matrix(predecessors)
        return distances, self.get_path(predecessors, adj_start_coord, adj_end_coord)
    
    def parabola_func(self, a, x1, x2, x_target):
        return a * (x_target - x1)*(x_target - x2)
    
    def create_parabola_path(self, start_pos, end_pos):
        dir = ((start_pos.x - end_pos.x) / 10) * -1    # number of points = 10
        x_target = start_pos.x

        while (True):
            x_target += dir
            if ((dir >= 0 and x_target >= end_pos.x) or (dir < 0 and x_target <= end_pos.x)):
                # additional point
                y_offset = self.parabola_func(-0.25, start_pos.x, end_pos.x, x_target)
                self.path.append((x_target, start_pos.y - y_offset))
                break

            y_offset = self.parabola_func(-0.25, start_pos.x, end_pos.x, x_target)
            self.path.append((x_target, start_pos.y - y_offset))

        
    def get_path(self, predecessors, adj_start_coord, adj_end_coord):

        self.path = []
        curr = adj_end_coord
        # while inserting, flip the coordinates so it is adjusted for pygame system

        while (curr is not None):
            self.path.insert(0, curr)#[curr[1], curr[0]]
            curr = predecessors[curr[0]][curr[1]]
            if (curr is None):
                break
            elif (curr[0] == adj_start_coord[0] and curr[1] == adj_start_coord[1]):
                self.path.insert(0, adj_start_coord)#[adj_start_coord[1], adj_start_coord[0]]
                break
        #print(self.path)
        return self.path
    
    def draw_path(self):
        if (len(self.path) > 1):
            points = []
            for point in self.path:
                # adjust points and let's put the point in the center
                points.append([point[0] * TILE_SIZE + (TILE_SIZE/2), point[1] * TILE_SIZE + (TILE_SIZE/2)])

            pygame.draw.lines(pygame.display.get_surface(), "red", False, points)
            #print(points)

class Tile:
    def __init__(self, pos):
        self.pos = pos

    def create_rect(self):
        return pygame.FRect((self.pos), (TILE_SIZE, TILE_SIZE))