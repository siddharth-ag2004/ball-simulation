import pygame
import pymunk
import pymunk.pygame_util
import math
import random
from pathlib import Path

class BouncingBallsGame:
    """Modern Pygame implementation with improved structure"""
    
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Display setup
        self.width, self.height = 1000, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Bouncing Balls in Hollow Circle")
        self.clock = pygame.time.Clock()
        
        # Load sound with error handling
        try:
            self.click_sound = pygame.mixer.Sound('bruh.mp3')
        except (pygame.error, FileNotFoundError):
            print("Warning: Sound file 'bruh.mp3' not found. Continuing without sound.")
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
            (75, 0, 130),   # Indigo
            (0, 0, 255),    # Blue
            (0, 255, 0),    # Green
            (255, 255, 0),  # Yellow
            (255, 127, 0),  # Orange
            (255, 0, 0),    # Red
        ]
        
        # Game state
        self.balls_count = 1
        self.colored_balls = []
        self.ball_base_radius = 10
        self.color_index = 0
        self.running = True
        
        # Mouse repulsion
        self.repulsion_radius = 100
        self.repulsion_strength = 1000
        
        # Initialize game
        self._create_circle_boundary()
        self._create_initial_ball()
        self._setup_collision_handler()
    
    def _create_circle_boundary(self):
        """Create hollow circle boundary using segments"""
        segments = []
        num_segments = 36
        
        for i in range(num_segments):
            angle1 = math.radians(i * 10)
            angle2 = math.radians((i + 1) * 10)
            
            start = (
                self.circle_center[0] + self.circle_radius * math.cos(angle1),
                self.circle_center[1] + self.circle_radius * math.sin(angle1),
            )
            end = (
                self.circle_center[0] + self.circle_radius * math.cos(angle2),
                self.circle_center[1] + self.circle_radius * math.sin(angle2),
            )
            
            segment = pymunk.Segment(self.space.static_body, start, end, 5)
            segment.elasticity = 1.0
            segment.friction = 0.0
            segment.collision_type = 1
            self.space.add(segment)
            segments.append(segment)
        
        return segments
    
    def _create_ball(self, position):
        """Create a new ball at the specified position"""
        # Calculate radius based on ball count
        ball_radius = self.ball_base_radius + self.balls_count * 1.3
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, ball_radius)
        
        body = pymunk.Body(mass, moment)
        body.position = position
        
        shape = pymunk.Circle(body, ball_radius)
        shape.elasticity = 1.0
        shape.friction = 0.0
        shape.collision_type = 2
        
        self.space.add(body, shape)
        
        # Assign color
        color = self.vibgyor_colors[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.vibgyor_colors)
        
        return ColoredBall(body, color, ball_radius)
    
    def _create_initial_ball(self):
        """Create the first ball"""
        initial_pos = (self.circle_center[0] - 50, self.circle_center[1] - 50)
        initial_ball = self._create_ball(initial_pos)
        self.colored_balls.append(initial_ball)
    
    def _setup_collision_handler(self):
        """Setup collision handler for ball-boundary collisions"""
        # Modern Pymunk API uses on_collision method
        self.space.on_collision(
            collision_type_a=1,
            collision_type_b=2,
            post_solve=self._on_collision
        )
    
    def _on_collision(self, arbiter, space, data):
        """Handle collision events"""
        # Play sound
        if self.click_sound:
            self.click_sound.play()
        
        # Randomly spawn new ball
        if random.random() < 1 / self.balls_count:
            new_ball = self._create_ball(self.circle_center)
            self.colored_balls.append(new_ball)
            self.balls_count += 1
        
        return True
    
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
            # Calculate distance
            dx = ball.body.position.x - mouse_pos[0]
            dy = ball.body.position.y - mouse_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Apply repulsion if within radius
            if distance < self.repulsion_radius and distance > 0:
                # Normalized force
                force_x = (dx / distance) * self.repulsion_strength
                force_y = (dy / distance) * self.repulsion_strength
                ball.body.apply_force_at_local_point((force_x, force_y), (0, 0))
    
    def _draw(self):
        """Render all game elements"""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw circle boundary
        pygame.draw.circle(
            self.screen,
            (255, 255, 255),
            self.circle_center,
            self.circle_radius,
            10
        )
        
        # Draw colored balls
        for ball in self.colored_balls:
            pos = ball.body.position
            pygame.draw.circle(
                self.screen,
                ball.color,
                (int(pos.x), int(pos.y)),
                int(ball.radius)
            )
        
        # Optional: Draw FPS counter
        fps = int(self.clock.get_fps())
        font = pygame.font.Font(None, 36)
        fps_text = font.render(f"FPS: {fps} | Balls: {self.balls_count}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            self._handle_events()
            
            # Apply physics
            self._apply_mouse_repulsion()
            
            # Render
            self._draw()
            
            # Update physics
            self.space.step(1 / 60.0)
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        # Cleanup
        pygame.quit()


class ColoredBall:
    """Data class for colored ball properties"""
    
    def __init__(self, body, color, radius):
        self.body = body
        self.color = color
        self.radius = radius


def main():
    """Entry point"""
    game = BouncingBallsGame()
    game.run()


if __name__ == "__main__":
    main()
