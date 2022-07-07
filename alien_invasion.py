import sys
from settings import Settings
import pygame
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


class AlienInvasion:
    """Загальний клас, що керує ресурсами та поведінкою гри"""

    def __init__(self):
        """Ініціалізувати гру створити ресурси гри"""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        #Створити екземпляр для збереження ігрової статистики
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        #Створити кнопку Play
        self.play_button = Button(self, "Play")

    def _update_bullets(self):
        """Оновити позицію куль та позбавитись старих куль"""
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_play_button(self, mouse_pos):
        """Розпочати нову гру, коли користувач натисне кнопку Play"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            #Анулювати статистику гри.
            self.settings.initialize_dynamic_settings()
            #Анулювати гральну статистику
            self.stats.reset_stats()
            self.stats.game_active = True

            #Позбавитись надлишку прибульців та куль
            self.aliens.empty()
            self.bullets.empty()

            #Створити новий флот та відцентрувати корабель
            self._create_fleet()
            self.ship.center_ship()

            #Приховати курсор миші
            pygame.mouse.set_visible(False)

    def _check_bullet_alien_collisions(self):
        """Реакція на зіткнення куль з прибульцями"""
        #Видалити всі кулі та прибульців, що зіткнулись
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        if not self.aliens:
            #Знищити наявні кулі та створити новий флот
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

    def _check_aliens_bottom(self):
        """Перевірити чи не досяг якийсь прибулець нижнього краю екрана."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                #Зреагувати так ніби корабель було підбито
                self._ship_hit()
                break

    def _create_fleet(self):
        """Створити флот прибульців"""
        #Створити прибульців та визначити їхню кількість у ряду
        #Відстань між прибульцями дорівнює ширині одного прибульця
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        #Визначити, яка кількість рядів прибульці поміщається на екрані
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                             (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        #Створити повний флот прибульців
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Створити прибульця та поставити його до ряду"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _update_aliens(self):
        """Перевірити чи флот знаходиться на краю,
        тоді оновити позиції всіх прибульців флоту"""
        self._check_fleet_edges()
        self.aliens.update()

        #Шукати зіткнення куль із прибульцями
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        #Шукати, чи котрийсь із прибульців досяг нижнього краю екрана
        self._check_aliens_bottom()

    def _ship_hit(self):
        """Реагувати на зіткнення прибульця з кораблем"""
        if self.stats.ships_left > 0:
            #Зменшити ships_left
            self.stats.ships_left -= 1
            #Позбавитись надлишку прибульців та куль
            self.aliens.empty()
            self.bullets.empty()
            #Створити новий флот та відцентрувати корабель
            self._create_fleet()
            self.bullets.empty()
            #Пауза
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_fleet_edges(self):
        """Реагує відповідно до того, чи досяг котрийсь
        із прибульців краю екрана"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break


    def _change_fleet_direction(self):
        """Спуск всього флоту та зміна його напрямку"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def run_game(self):
        """Розпочати головний цикл гри"""

        def _check_events():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)
                elif event.type == pygame.KEYDOWN:
                    _check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    _check_keyup_events(event)

        def _check_keydown_events(event):
            """Реагувати на натискання клавіш"""
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = True
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = True
            elif event.key == pygame.K_q:
                sys.exit()
            elif event.key == pygame.K_SPACE:
                _fire_bullet()

        def _check_keyup_events(event):
            """Реагувати, коли клавіша не натиснута"""
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = False
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = False

        def _fire_bullet():
            """Створити нову кулю та додати її до групи куль"""
            if len(self.bullets) < self.settings.bullets_allowed:
                new_bullet = Bullet(self)
                self.bullets.add(new_bullet)

        def _update_screen():
            """Оновити зображення на екрані та перемкнутись на новий екран"""
            self.screen.fill(self.settings.bg_color)
            self.ship.blitme()
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            self.aliens.draw(self.screen)

            #Намалювати інформацію про рахунок
            self.sb.show_score()

            #Намалювати кнопку плей, якщо гра не активна
            if not self.stats.game_active:
                self.play_button.draw_button()

            pygame.display.flip()

        while True:
            _check_events()
            _update_screen()
            self.bullets.update()
            if self.stats.game_active:
                self.ship.update()
                self._update_aliens()
                self._update_bullets()


if __name__ == '__main__':
    #Створити екземпляр гри та запустити гру.
    ai = AlienInvasion()
    ai.run_game()
