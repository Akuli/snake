#!/usr/bin/env python3

import collections
import random
import tkinter as tk


binding2direction = {
    # tkinter_binding: (dx, dy)
    'Up': (0, -1),
    'Down': (0, 1),
    'Left': (-1, 0),
    'Right': (1, 0),
}


class SnakeGame(tk.Frame):

    def __init__(self, parentwidget, width, height, scale):
        self.width = width
        self.height = height
        self.scale = scale

        # deque maxlen is useless for this because it can't be changed
        # after creating the deque :(
        self.snake_body = collections.deque((x, height//2) for x in range(5))
        self.previous_direction = self.next_direction = binding2direction['Up']
        self.game_over = False
        self.food = self.make_food()

        self.frame = tk.Frame(parentwidget)
        self.canvas = tk.Canvas(
            self.frame, width=width*scale, height=height*scale)
        self.canvas.pack(fill='both', expand=True)
        self.statusbar = tk.Label(self.frame, relief='sunken')
        self.statusbar.pack(fill='x')

        self.item_ids = {}    # {(x, y): item_id}
        for x in range(width):
            for y in range(height):
                # (x_start, y_start, x_end, y_end)
                coords = (x * self.scale, y * self.scale,
                          (x+1) * self.scale, (y+1) * self.scale)
                self.item_ids[(x, y)] = self.canvas.create_rectangle(*coords)

        self.move(schedule_again=True)
        self.refresh()

    # FIXME: this gets stuck forever if there's no free space
    def make_food(self):
        # why doesn't python have do-while :(
        food = (random.randrange(self.width), random.randrange(self.height))
        while food in self.snake_body:
            food = (random.randrange(self.width),
                    random.randrange(self.height))
        return food

    def on_key(self, event):
        if self.game_over:
            return

        new_direction = binding2direction[event.keysym]

        # can't turn around
        opposite = (-self.previous_direction[0], -self.previous_direction[1])
        if new_direction != opposite:
            self.next_direction = new_direction
            self.move()

    def move(self, schedule_again=False):
        if self.game_over:
            return

        last_x, last_y = self.snake_body[-1]
        dx, dy = self.previous_direction = self.next_direction
        x = (last_x + dx) % self.width
        y = (last_y + dy) % self.height

        if (x, y) in self.snake_body:
            self.snake_body.append((x, y))
            self.refresh()

            self.game_over = True
            self.canvas.create_text(
                self.width * self.scale // 2, self.height * self.scale // 2,
                text="Game Over :(", font="TkDefaultFont 50",
                fill='red', justify="center")
            return

        self.snake_body.append((x, y))
        if self.food == (x, y):
            self.food = self.make_food()
        else:
            self.snake_body.popleft()

        self.refresh()
        if schedule_again:
            sleeptime = int(random.random() * 1000 / len(self.snake_body))
            self.canvas.after(sleeptime, self.move, True)

    def refresh(self):
        self.statusbar['text'] = "Score: " + str(len(self.snake_body))
        for coords, item_id in self.item_ids.items():
            if coords == self.food:
                color = 'red'
            elif coords in self.snake_body:
                color = 'black'
            else:
                color = 'white'
            self.canvas.itemconfig(item_id, fill=color)


def main():
    root = tk.Tk()

    game = SnakeGame(root, 15, 10, scale=40)
    game.frame.pack(fill='both', expand=True)
    for binding in binding2direction:
        root.bind('<%s>' % binding, game.on_key)

    root.mainloop()

if __name__ == '__main__':
    main()
