import math
import pygame
from queue import PriorityQueue

WIDTH = 1800
ROWS = 50
GAP = WIDTH // ROWS

win = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Visualisation")

END = (255, 0, 0)               # red
START = (0, 255, 0)             # green
OPEN = (0, 0, 255)            # blue
YELLOW = (255, 255, 0)            # yellow
BLANK = (255, 255, 255)         # white
WALL = (0, 0, 0)                # black
GRID_LINE = (128, 128, 128)     # grey
ORANGE = (255, 165, 0)            # orange

PATH = (179, 66, 245)          # purple
CLOSED = (64, 224, 208)      # turquoise

class Node:
    def __init__(self, pos: tuple):
        self.x = pos[0]
        self.y = pos[1]
        self.display_x = self.x * GAP
        self.display_y = self.y * GAP
        self.colour = BLANK
        self.neighbours = set()
        self.total_rows = ROWS

    def get_pos(self) -> tuple:
        return self.x, self.y

    def set_type(self, node_type: tuple) -> None:
        self.colour = node_type

    def get_type(self) -> tuple:
        return self.colour

    def draw(self) -> None:
        pygame.draw.rect(win, self.colour, (self.display_x, self.display_y, GAP, GAP))

    def set_neighbours(self, grid: list) -> None:
        self.neighbours = set()
        if self.x < ROWS - 1 and grid[self.x + 1][self.y].get_type() != WALL: # down
            self.neighbours.add(grid[self.x + 1][self.y])

        if self.x > 0 and grid[self.x - 1][self.y].get_type() != WALL: # up
            self.neighbours.add(grid[self.x - 1][self.y])

        if self.y < ROWS - 1 and grid[self.x][self.y + 1].get_type() != WALL: # right
            self.neighbours.add(grid[self.x][self.y + 1])

        if self.y > 0 and grid[self.x][self.y - 1].get_type() != WALL: # left
            self.neighbours.add(grid[self.x][self.y - 1])

    
def get_dist(node1: Node, node2: Node) -> int:
    manhattan_dist = abs(node1.x - node2.x) + abs(node1.y - node2.y)
    return manhattan_dist

def reconstruct_path(came_from: dict, current: Node, draw: callable) -> None:
    while current in came_from:
        current = came_from[current]
        current.set_type(PATH)
        draw()

def make_grid():
    grid = []
    for i in range(ROWS):
        grid.append([])
        for j in range(ROWS):
            grid[i].append(Node((i, j)))

    return grid

def draw_grid() -> None:
    for i in range(ROWS):
        pygame.draw.line(win, GRID_LINE, (0, i * GAP), (WIDTH, i * GAP))
        for j in range(ROWS):
            pygame.draw.line(win, GRID_LINE, (j * GAP, 0), (j * GAP, WIDTH))

def draw(grid: list) -> None:
    win.fill(BLANK)
    for row in grid:
        for node in row:
            node.draw()

    draw_grid()
    pygame.display.update()

def get_clicked_pos(mouse_pos: tuple) -> tuple:
    y, x = mouse_pos
    row, col = y // GAP, x // GAP
    return row, col

def left_click(start_node: Node, end_node: Node, clicked_node: Node) -> tuple:
    if not start_node and clicked_node != end_node:
        start_node = clicked_node
        start_node.set_type(START)
    elif not end_node and clicked_node != start_node:
        end_node = clicked_node
        end_node.set_type(END)
    elif clicked_node != start_node and clicked_node != end_node:
        clicked_node.set_type(WALL)
    return start_node, end_node, clicked_node

def right_click(start_node: Node, end_node: Node, clicked_node: Node) -> tuple:
    if clicked_node.get_type() == START: start_node = None
    elif clicked_node.get_type() == END: end_node = None
    clicked_node.set_type(BLANK)
    return start_node, end_node, clicked_node

def a_star(draw: callable, grid: list, start_node: Node, end_node: Node) -> bool:
    count = 0
    run = True
    open_node_queue = PriorityQueue()
    open_node_queue.put((0, count, start_node)) # f-score, count, node
    open_node_set, came_from = {start_node}, {}
    g_score = f_score = {node: float("inf") for row in grid for node in row}
    g_score[start_node], f_score[start_node] = 0, get_dist(start_node, end_node)

    while not open_node_queue.empty() and run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False

        current = open_node_queue.get()[2]
        open_node_set.remove(current)

        if current == end_node:
            reconstruct_path(came_from, end_node, draw)
            start_node.set_type(START)
            end_node.set_type(END)
            return True, run

        for neighbour in current.neighbours:
            temp_g_score =  g_score[current] + 1

            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + get_dist(neighbour, end_node)
                if neighbour not in open_node_set:
                    count += 1
                    open_node_queue.put((f_score[neighbour], count, neighbour))
                    open_node_set.add(neighbour)
                    neighbour.set_type(OPEN)

        draw()

        if current != start_node:
            current.set_type(CLOSED)

    return False, run

def main():
    grid = make_grid()
    start_node, end_node = None, None
    run, started = True, False

    while run:
        draw(grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if started: continue    # so user cannot click/draw once pathfinding starts

            if pygame.mouse.get_pressed()[0] or pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                clicked_node = grid[row][col]
                if pygame.mouse.get_pressed()[0]:   # if left click
                    start_node, end_node, clicked_node = left_click(start_node, end_node, clicked_node)
                elif pygame.mouse.get_pressed()[2]: # if right click
                    start_node, end_node, clicked_node = right_click(start_node, end_node, clicked_node)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    started = True
                    for row in grid:
                        for node in row:
                            node.set_neighbours(grid)

                    if not a_star(lambda: draw(grid), grid, start_node, end_node)[1]:
                        run = False

    pygame.quit()

main()