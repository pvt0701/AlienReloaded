import sys
from settings import Settings
import pygame
from ship import Ship

class AlienInvasion:
    """Загальний клас, що керує ресурсами та поведінкою гри"""

    def __init__(self):
        """Ініціалізувати гру створити ресурси гри"""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        self.ship = Ship(self)

    def run_game(self):
        """Розпочати головний цикл гри"""

        def _check_events():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

        def _update_screen():
            """Оновити зображення на екрані та перемкнутись на новий екран"""
            self.screen.fill(self.settings.bg_color)
            self.ship.blitme()

            pygame.display.flip()

        while True:
            _check_events()
            _update_screen()

if __name__ == '__main__':
    #Створити екземпляр гри та запустити гру.
    ai = AlienInvasion()
    ai.run_game()