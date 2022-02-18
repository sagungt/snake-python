import tkinter as tk
import numpy as np
import heapq
from random import randint

WIDTH = 600  # pixel
HEIGHT = 600  # pixel
BLOCK = 10  # block size in pixel
SPEED = 10  # millisecond
EPOCH = 10


class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry(f'{WIDTH + 5}x{HEIGHT + 5}+0+0')
        self.root.resizable(0, 0)
        self.__init()
        self.snake = Snake()
        self.grid = np.zeros((WIDTH // BLOCK, HEIGHT // BLOCK), dtype=np.int32)
        self.randomFood()
        self.find_path = False
        self.score = 0
        self.scores = []
        self.loop = self.canvas.after(SPEED, self.gameLoop)

    def __init(self):
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack()
        self.canvas = tk.Canvas(self.canvas_frame, width=WIDTH, height=HEIGHT,
                                highlightthickness=5, highlightbackground="black")
        self.canvas.pack()
        self.root.bind('<Key>', self.changeDirection)

    def restart(self):
        self.snake = Snake()
        self.grid = np.zeros((WIDTH // BLOCK, HEIGHT // BLOCK), dtype=np.int32)
        self.loop = self.canvas.after(SPEED, self.gameLoop)
        self.find_path = False
        self.score = 0

    def changeDirection(self, event):
        if event.keycode == 38 and not self.dy == BLOCK:
            self.snake.direction = Snake.UP
        elif event.keycode == 39 and not self.dx == -BLOCK:
            self.snake.direction = Snake.RIGHT
        elif event.keycode == 37 and not self.dx == BLOCK:
            self.snake.direction = Snake.LEFT
        elif event.keycode == 40 and not self.dy == -BLOCK:
            self.snake.direction = Snake.DOWN
        else:
            pass

    def clearCanvas(self):
        self.canvas.delete('all')

    def generateGrid(self):
        self.canvas.delete('grid_line')

        for w in range(0, WIDTH, BLOCK):
            self.canvas.create_line([(w, 0), (w, WIDTH)], tag='grid_line',
                                    fill='white', width=0.01)

        for h in range(0, HEIGHT, BLOCK):
            self.canvas.create_line([(0, h), (HEIGHT, h)], tag='grid_line',
                                    fill='white', width=0.01)

    def drawSnake(self):
        multiply = 1
        for i, snake in enumerate(self.snake.body):
            color = (0 * multiply, i * multiply, 0 * multiply)
            self.canvas.create_rectangle((snake['x'], snake['y']), (
                snake['x'] + BLOCK, snake['y'] + BLOCK), outline='#%02x%02x%02x' % color, fill='#%02x%02x%02x' % color)
            # if i == 0:
            #     self.canvas.create_oval(
            #         (snake['x']+15, snake['y']+15), (snake['x']+25, snake['y']+25), outline='white', fill='white')
            # # else:
            # #     self.canvas.create_oval(
            # #         (snake['x']+5, snake['y']+5), (snake['x']+15, snake['y']+15), outline='green', fill='green')
            # #     self.canvas.create_oval(
            # #         (snake['x']+20, snake['y']+30), (snake['x']+25, snake['y']+35), outline='green', fill='green')
            # #     self.canvas.create_oval(
            # #         (snake['x']+30, snake['y']+20), (snake['x']+35, snake['y']+25), outline='green', fill='green')
            self.grid[snake['x'] // BLOCK][snake['y'] // BLOCK] = 1

    def moveSnake(self):
        head = {'x': self.snake.body[0]['x'] +
                self.snake.direction[0], 'y': self.snake.body[0]['y'] + self.snake.direction[1]}
        self.snake.body.insert(0, head)
        has_eaten = (self.snake.body[0]['x'], self.snake.body[0]
                     ['y']) == (self.food_x, self.food_y)
        if has_eaten:
            self.randomFood()
            self.score += 1
        else:
            tail = self.snake.body.pop()
            self.grid[tail['x'] // BLOCK][tail['y'] // BLOCK] = 0

    def gameLoop(self):
        if self.gameOver():
            self.canvas.after_cancel(self.loop)
            print('score :', self.score)
            self.scores.append(self.score)
            if len(self.scores) < EPOCH:
                self.restart()
            else:
                self.canvas.after_cancel(self.loop)
                average = np.mean(self.scores, dtype=np.int32)
                print(f'averages :', average)
        else:
            self.clearCanvas()
            self.generateGrid()
            if self.find_path == False:
                self.findPath()
                self.drawSnake()
                self.drawFood()
                self.canvas.update()
                self.loop = self.canvas.after(SPEED, self.gameLoop)
            else:
                self.drawSnake()
                self.drawFood()
                self.autoMove()
                self.moveSnake()
                self.canvas.update()
                self.loop = self.canvas.after(SPEED, self.gameLoop)

    def gameOver(self):
        # body collision
        if len(self.snake.body) > 1:
            for i in range(2, len(self.snake.body)):
                if self.snake.body[i] == self.snake.body[0]:
                    return True
        # wall collision
        hit_left_wall = self.snake.body[0]['x'] < 0
        hit_top_wall = self.snake.body[0]['y'] < 0
        hit_right_wall = self.snake.body[0]['x'] > WIDTH - BLOCK
        hit_bottom_wall = self.snake.body[0]['y'] > WIDTH - BLOCK
        return hit_bottom_wall or hit_left_wall or hit_right_wall or hit_top_wall

    def drawFood(self):
        self.canvas.create_rectangle((self.food_x, self.food_y), (
            self.food_x + BLOCK, self.food_y + BLOCK), outline='red', fill='red')

    def randomFood(self):
        self.food_x = randint(1, (WIDTH/BLOCK) - 2) * BLOCK
        self.food_y = randint(1, (HEIGHT/BLOCK) - 2) * BLOCK
        # Regenerate food if food location is in body location
        if (self.food_x, self.food_y) in [(body['x'], body['y']) for body in self.snake.body]:
            self.randomFood()
        # Generate again if food has eaten
        for snake in self.snake.body:
            has_eaten = (snake['x'], snake['y']) == (self.food_x, self.food_y)
            if has_eaten:
                self.randomFood()
                self.find_path = False

    def start(self):
        self.root.mainloop()

    def heuristic(self, start, goal):
        return np.sqrt((goal[0] - start[0]) ** 2 + (goal[1] - start[1]) ** 2)

    def astar(self, start, goal):
        neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        close_set = set()
        came_from = {}

        gscore = {start: 0}
        fscore = {start: self.heuristic(start, goal)}

        oheap = []
        heapq.heappush(oheap, (fscore[start], start))

        while oheap:
            current = heapq.heappop(oheap)[1]
            # Goal point has founded
            if current == goal:
                data = []
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                data.reverse()
                return data

            close_set.add(current)

            for i, j in neighbors:
                neighbor = current[0] + i, current[1] + j
                tentative_g_score = gscore[current] + \
                    self.heuristic(current, neighbor)

                # Skip if neigbor is wall or obstacle grid
                if 0 <= neighbor[0] < self.grid.shape[0]:
                    if 0 <= neighbor[1] < self.grid.shape[1]:
                        if self.grid[neighbor[0]][neighbor[1]] >= 1:
                            continue
                    else:
                        continue
                else:
                    continue

                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue

                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + \
                        self.heuristic(neighbor, goal)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
        return []

    def autoMove(self):
        if self.path:
            next_path = self.path.pop(0)
            self.snake.direction = (next_path[0] * BLOCK - self.snake.body[0]['x'],
                                    next_path[1] * BLOCK - self.snake.body[0]['y'])
            for i in self.path[0:-1]:
                self.canvas.create_rectangle((i[0] * BLOCK, i[1] * BLOCK),
                                             (i[0] * BLOCK + BLOCK, i[1] * BLOCK + BLOCK),
                                             outline='yellow', fill='yellow')
        else:
            self.find_path = False

    def findPath(self):
        head = tuple([self.snake.body[0]['x'] // BLOCK,
                      self.snake.body[0]['y'] // BLOCK])
        food = tuple([self.food_x // BLOCK, self.food_y // BLOCK])
        self.path = self.astar(head, food)
        for i in self.path:
            self.canvas.create_rectangle((i[0] * BLOCK, i[1] * BLOCK), (
                i[0] * BLOCK + BLOCK, i[1] * BLOCK + BLOCK), outline='yellow', fill='yellow')
        self.find_path = True


class Snake:
    LEFT = (-BLOCK, 0)
    RIGHT = (BLOCK, 0)
    UP = (0, -BLOCK)
    DOWN = (0, BLOCK)

    def __init__(self):
        self.body = [
            {'x': 280, 'y': 280},
        ]
        self.direction = (0, 0)


if __name__ == '__main__':
    x = SnakeGame()
    x.start()
