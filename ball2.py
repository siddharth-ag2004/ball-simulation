import pygame
import pymunk
import pymunk.pygame_util
import math
import random

ELASTICITY = 1.0


class BouncingBallsGame:
    """Modified Pygame implementation with escape mechanics"""

    def __init__(self):
        # Initialize Pygame
        pygame.init()

        # Display setup
        self.width, self.height = 1000, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Bouncing Balls - Escape the Circle")
        self.clock = pygame.time.Clock()

        # Load sound with error handling
        try:
            self.click_sound = pygame.mixer.Sound("faaa.mp3")
        except (pygame.error, FileNotFoundError):
            self.click_sound = None

        # Physics setup
        self.space = pymunk.Space()
        self.space.gravity = (0, 500)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        # Circle boundary properties
        self.circle_radius = 380
        self.circle_center = (self.width // 2, self.height // 2)

        # VIBGYOR colors
        self.vibgyor_colors = [
            (148, 0, 211),  # Violet
            (75, 0, 130),  # Indigo
            (0, 0, 255),  # Blue
            (0, 255, 0),  # Green
            (255, 255, 0),  # Yellow
            (255, 127, 0),  # Orange
            (255, 0, 0),  # Red
        ]

        # Game state
        self.colored_balls = []
        self.ball_fixed_radius = 15  # Constant size
        self.color_index = 0
        self.running = True

        # Mouse repulsion
        self.repulsion_radius = 150
        self.repulsion_strength = -15000

        # Initialize game
        self._create_circle_boundary()
        self._create_ball(self.circle_center)  # Start with 1 ball
        self.ring_body.angular_velocity = 0.5

    def _create_circle_boundary(self):
        """Create rotating hollow circle boundary with a GAP"""
        # 1. Create a Kinematic Body for the ring
        # Kinematic bodies can be moved/rotated by code but push dynamic bodies
        self.ring_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.ring_body.position = self.circle_center # Set body to screen center
        self.space.add(self.ring_body)

        segments = []
        num_segments = 60
        step = 360 / num_segments
        
        for i in range(num_segments):
            angle_deg = i * step
            
            # The Gap logic
            if 0 < angle_deg < 40: 
                continue
                
            angle1 = math.radians(angle_deg)
            angle2 = math.radians((i + 1) * step)
            
            # 2. Define vertices relative to the BODY (0,0), not screen center
            # We don't add self.circle_center[0] here because the body is already there
            start = (
                self.circle_radius * math.cos(angle1),
                self.circle_radius * math.sin(angle1),
            )
            end = (
                self.circle_radius * math.cos(angle2),
                self.circle_radius * math.sin(angle2),
            )
            
            # 3. Attach segment to the rotating ring_body
            segment = pymunk.Segment(self.ring_body, start, end, 5)
            segment.elasticity = 0.9
            segment.friction = 0.5
            self.space.add(segment)
            segments.append(segment)
        
        return segments 

    def _create_ball(self, position):
        """Create a new ball with CONSTANT size"""
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, self.ball_fixed_radius)

        body = pymunk.Body(mass, moment)
        body.position = position

        vx = random.randint(-400, 400) 
        vy = random.randint(-400, 400)
        body.velocity = (vx, vy)

        shape = pymunk.Circle(body, self.ball_fixed_radius)
        shape.elasticity = ELASTICITY
        shape.friction = 0

        self.space.add(body, shape)

        # Assign color
        color = self.vibgyor_colors[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.vibgyor_colors)

        ball_obj = ColoredBall(body, color, self.ball_fixed_radius)
        self.colored_balls.append(ball_obj)
        return ball_obj

    def _handle_escaped_balls(self):
        """Check if balls are outside the boundary, remove them, and spawn 2 new ones"""
        balls_to_remove = []

        for ball in self.colored_balls:
            # Calculate distance from center
            dx = ball.body.position.x - self.circle_center[0]
            dy = ball.body.position.y - self.circle_center[1]
            distance = math.sqrt(dx**2 + dy**2)

            # If distance is significantly larger than radius (ball is outside)
            if distance > self.circle_radius + 50:
                balls_to_remove.append(ball)

        for ball in balls_to_remove:
            # Remove from physics space
            self.space.remove(ball.body, list(ball.body.shapes)[0])
            # Remove from our list
            self.colored_balls.remove(ball)

            # Play sound on escape/multiply
            if self.click_sound:
                self.click_sound.play()

            # Spawn 2 new balls at the center
            self._create_ball(self.circle_center)
            self._create_ball(self.circle_center)

    def _handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    # Reverse gravity
                    self.space.gravity = (0, -self.space.gravity[1])
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def _apply_mouse_repulsion(self):
        """Apply repulsion force from mouse to balls"""
        mouse_pos = pygame.mouse.get_pos()

        for ball in self.colored_balls:
            dx = ball.body.position.x - mouse_pos[0]
            dy = ball.body.position.y - mouse_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)

            if distance < self.repulsion_radius and distance > 0:
                force_x = (dx / distance) * self.repulsion_strength
                force_y = (dy / distance) * self.repulsion_strength
                ball.body.apply_force_at_local_point((force_x, force_y), (0, 0))

    def _draw(self):
        """Render all game elements"""
        self.screen.fill((0, 0, 0))
        
        # Draw rotating circle boundary
        # We iterate over shapes attached to the ring body
        for shape in self.ring_body.shapes:
            if isinstance(shape, pymunk.Segment):
                # Convert local body coordinates to world coordinates for drawing
                # shape.a is start point, shape.b is end point
                p1 = self.ring_body.local_to_world(shape.a)
                p2 = self.ring_body.local_to_world(shape.b)
                
                pygame.draw.line(self.screen, (255, 255, 255), p1, p2, 5)

        # Draw colored balls
        for ball in self.colored_balls:
            pos = ball.body.position
            pygame.draw.circle(
                self.screen,
                ball.color,
                (int(pos.x), int(pos.y)),
                int(ball.radius)
            )
        
        # Stats
        fps = int(self.clock.get_fps())
        font = pygame.font.Font(None, 36)
        text = font.render(f"FPS: {fps} | Balls: {len(self.colored_balls)}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

    def run(self):
        """Main game loop"""
        while self.running:
            self._handle_events()
            self._apply_mouse_repulsion()
            self._handle_escaped_balls()  # New logic here

            self._draw()

            # Physics Step
            self.space.step(1 / 60.0)
            self.ring_body.angular_velocity += 0.001

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


class ColoredBall:
    """Data class for colored ball properties"""

    def __init__(self, body, color, radius):
        self.body = body
        self.color = color
        self.radius = radius


def main():
    game = BouncingBallsGame()
    game.run()


if __name__ == "__main__":
    main()
