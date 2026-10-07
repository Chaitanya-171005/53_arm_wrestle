import math
import random
import pygame


class GameEngine:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.arm_position = 0.0
        self.target_limit = 100.0
        self.last_key = None
        
        self.stamina = 100.0
        self.max_stamina = 100.0
        
        self.winner = None
        self.game_state = "PLAYING"
        self.ai_strength = 0.35

        self.ai_phase = "NORMAL"
        self.ai_phase_start = pygame.time.get_ticks()
        self.ai_phase_duration = random.randint(2500, 4500)

        self.counter_window_start = None
        self.counter_window_duration = 750
        self.counter_active_until = 0
        self.counter_duration = 3000
        self.counter_push_multiplier = 2.0
        self.counter_stamina_recovery = 1.6
        
        self.font_big = pygame.font.SysFont(None, 44)
        self.font_med = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            if self.stamina <= 10:
                return

            current_time = pygame.time.get_ticks()

            if event.key == pygame.K_LEFT:
                if self.last_key != pygame.K_LEFT:
                    push_strength = 4.2

                    if (self.counter_active_until > current_time or
                            (self.counter_window_start is not None and
                             current_time - self.counter_window_start <= self.counter_window_duration)):
                        if self.counter_active_until <= current_time:
                            self.counter_active_until = current_time + self.counter_duration
                            self.counter_window_start = None
                        push_strength *= self.counter_push_multiplier

                    self.arm_position -= push_strength
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_LEFT

            elif event.key == pygame.K_RIGHT:
                if self.last_key != pygame.K_RIGHT:
                    push_strength = 4.2

                    if (self.counter_active_until > current_time or
                            (self.counter_window_start is not None and
                             current_time - self.counter_window_start <= self.counter_window_duration)):
                        if self.counter_active_until <= current_time:
                            self.counter_active_until = current_time + self.counter_duration
                            self.counter_window_start = None
                        push_strength *= self.counter_push_multiplier

                    self.arm_position -= push_strength
                    self.stamina = max(0.0, self.stamina - 2.0)
                    self.last_key = pygame.K_RIGHT

    def update(self):
        if self.game_state != "PLAYING":
            return

        current_time = pygame.time.get_ticks()

        if current_time - self.ai_phase_start >= self.ai_phase_duration:
            if self.ai_phase == "NORMAL":
                self.ai_phase = "SURGE"
                self.ai_phase_duration = random.randint(700, 1300)
                self.counter_window_start = None

            elif self.ai_phase == "SURGE":
                self.ai_phase = "COOLDOWN"
                self.ai_phase_duration = random.randint(1500, 2500)
                self.counter_window_start = current_time

            else:
                self.ai_phase = "NORMAL"
                self.ai_phase_duration = random.randint(2500, 4500)
                self.counter_window_start = None

            self.ai_phase_start = current_time

        ai_variance = random.uniform(0.3, 1.0)

        if self.ai_phase == "SURGE":
            ai_force = self.ai_strength * 2.2

        elif self.ai_phase == "COOLDOWN":
            ai_force = self.ai_strength * 0.35

        else:
            ai_force = self.ai_strength

        self.arm_position += ai_force * ai_variance

        recovery_rate = (
            self.counter_stamina_recovery
            if self.counter_active_until > current_time
            else 0.8
        )

        if self.stamina < self.max_stamina:
            self.stamina = min(
                self.max_stamina,
                self.stamina + recovery_rate
            )

        if self.arm_position <= -self.target_limit:
            self.winner = "PLAYER"
            self.game_state = "GAME_OVER"

        elif self.arm_position >= self.target_limit:
            self.winner = "COMPUTER"
            self.game_state = "GAME_OVER"

    def reset(self):
        self.arm_position = 0.0
        self.stamina = 100.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

        self.ai_phase = "NORMAL"
        self.ai_phase_start = pygame.time.get_ticks()
        self.ai_phase_duration = random.randint(2500, 4500)

        self.counter_window_start = None
        self.counter_active_until = 0

    def render(self, screen):
        screen.fill((25, 28, 35))

        title_surf = self.font_big.render(
            "ARM WRESTLE SHOWDOWN",
            True,
            (240, 240, 240)
        )
        screen.blit(
            title_surf,
            (self.width // 2 - title_surf.get_width() // 2, 12)
        )

        player_header = self.font_med.render(
            "PLAYER",
            True,
            (80, 160, 255)
        )

        computer_header = self.font_med.render(
            "COMPUTER",
            True,
            (255, 100, 80)
        )

        screen.blit(player_header, (60, 55))
        screen.blit(computer_header, (self.width - 150, 55))

        table_rect = pygame.Rect(
            40,
            100,
            self.width - 80,
            310
        )

        pygame.draw.rect(
            screen,
            (110, 50, 15),
            table_rect,
            border_radius=14
        )

        pygame.draw.rect(
            screen,
            (70, 30, 8),
            table_rect,
            width=5,
            border_radius=14
        )

        pygame.draw.line(
            screen,
            (45, 18, 4),
            (self.width // 2, 100),
            (self.width // 2, 410),
            4
        )

        offset_x = (
            self.arm_position / self.target_limit
        ) * 95

        hand_x = (
            self.width // 2
        ) + int(offset_x)

        hand_y = 235

        p_shoulder = (70, 330)
        p_elbow = (140, 215)

        c_shoulder = (self.width - 70, 330)
        c_elbow = (self.width - 140, 215)

        pygame.draw.line(
            screen,
            (200, 145, 110),
            p_shoulder,
            p_elbow,
            32
        )

        pygame.draw.line(
            screen,
            (215, 160, 125),
            p_elbow,
            (hand_x, hand_y),
            26
        )

        pygame.draw.circle(
            screen,
            (185, 130, 95),
            p_elbow,
            18
        )

        pygame.draw.line(
            screen,
            (170, 110, 85),
            c_shoulder,
            c_elbow,
            32
        )

        pygame.draw.line(
            screen,
            (185, 125, 95),
            c_elbow,
            (hand_x, hand_y),
            26
        )

        pygame.draw.circle(
            screen,
            (150, 95, 70),
            c_elbow,
            18
        )

        pygame.draw.circle(
            screen,
            (225, 175, 140),
            (hand_x, hand_y),
            24
        )

        pygame.draw.circle(
            screen,
            (160, 115, 85),
            (hand_x, hand_y),
            24,
            width=3
        )

        stamina_label = self.font_med.render(
            "STAMINA",
            True,
            (220, 220, 220)
        )

        screen.blit(
            stamina_label,
            (40, 445)
        )

        stamina_bg = pygame.Rect(
            140,
            448,
            240,
            22
        )

        stamina_fill = pygame.Rect(
            140,
            448,
            int(
                240 * (
                    self.stamina /
                    self.max_stamina
                )
            ),
            22
        )

        pygame.draw.rect(
            screen,
            (45, 50, 60),
            stamina_bg,
            border_radius=6
        )

        bar_color = (
            (60, 210, 100)
            if self.stamina > 25
            else (220, 60, 60)
        )

        pygame.draw.rect(
            screen,
            bar_color,
            stamina_fill,
            border_radius=6
        )

        # Flash a warning while the AI is in its Surge phase.
        if self.ai_phase == "SURGE":
            current_time = pygame.time.get_ticks()

            if (current_time // 250) % 2 == 0:
                surge_surf = self.font_big.render(
                    "AI Surge!",
                    True,
                    (255, 210, 60)
                )

                screen.blit(
                    surge_surf,
                    (
                        self.width // 2
                        - surge_surf.get_width() // 2,
                        65
                    )
                )

        # Show that player input is blocked when stamina is too low.
        if self.stamina <= 10:
            exhausted_surf = self.font_med.render(
                "Exhausted",
                True,
                (240, 80, 80)
            )

            screen.blit(
                exhausted_surf,
                (400, 445)
            )

        # Show the temporary counter-surge bonus while active.
        if self.counter_active_until > pygame.time.get_ticks():
            counter_surf = self.font_med.render(
                "Counter!",
                True,
                (80, 240, 100)
            )

            screen.blit(
                counter_surf,
                (500, 445)
            )

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 200)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            win_text = (
                "PLAYER WINS THE MATCH!"
                if self.winner == "PLAYER"
                else "COMPUTER WINS!"
            )

            color = (
                (80, 240, 100)
                if self.winner == "PLAYER"
                else (240, 80, 80)
            )

            text_surf = self.font_big.render(
                win_text,
                True,
                color
            )

            screen.blit(
                text_surf,
                (
                    self.width // 2
                    - text_surf.get_width() // 2,
                    self.height // 2 - 45
                )
            )

            restart_surf = self.font_med.render(
                "Press [R] to Rematch",
                True,
                (240, 240, 240)
            )

            screen.blit(
                restart_surf,
                (
                    self.width // 2
                    - restart_surf.get_width() // 2,
                    self.height // 2 + 10
                )
            )