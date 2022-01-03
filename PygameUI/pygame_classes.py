import pygame

class Button:
    def __init__(self, screen, x, y, width, height, on_click, color, rounded=0, border=0, border_color=(0, 0, 0)):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.on_click = on_click
        self.color = color
        self.rounded = rounded
        self.border = border
        self.border_color = border_color

    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height), border_radius=self.rounded)
        if self.border != 0:
            pygame.draw.rect(self.screen, self.border_color, (self.x, self.y, self.width, self.height), border_radius=self.rounded, width=int(self.border * 2))

    def check_click(self, x, y):
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            self.on_click()
            return True
        return False


class ButtonWithText(Button):
    def __init__(self, screen, x, y, width, height, on_click, color, font, text="", rounded=0,  border=0, border_color=None, text_color=(255, 255, 255)):
        super().__init__(screen, x, y, width, height, on_click, color, rounded, border, border_color)
        self.text = text
        self.font = font
        self.text_color = text_color

    def draw(self):
        super().draw()
        text_obj = self.font.render(self.text, 1, self.text_color)
        text_width, text_height = text_obj.get_width(), text_obj.get_height()
        self.screen.blit(text_obj, (self.x + self.width / 2 - text_width / 2, self.y + self.height / 2 - text_height / 2))


class DefaultButton(ButtonWithText):
    def __init__(self, screen, x, y, width, height, on_click, font, text):
        super().__init__(screen, x, y, width, height, on_click, (70, 70, 70), font, text, 7,  1.5, (10, 10, 10))
