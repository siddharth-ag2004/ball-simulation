import pygame
import pymunk
import pymunk.pygame_util
import math
import random

# Pygame and Pymunk initialization
pygame.init()
width, height = 1000, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bouncing Balls in Hollow Circle")
clock = pygame.time.Clock()

# Pygame Sound Initialization
click_sound = pygame.mixer.Sound('bruh.mp3')  # Make sure to have the sound file in the correct path

# Pymunk space setup
space = pymunk.Space()
space.gravity = (0, 500)

# Drawing helper
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Create a hollow circle boundary
circle_radius = 380
circle_center = (width // 2, height // 2)

# VIBGYOR Colors
VIBGYOR_COLORS = [
    (148, 0, 211),  # Violet
    (0, 0, 255),  # Blue
    (0, 255, 0),  # Green
    (255, 255, 0),  # Yellow
    (255, 127, 0),  # Orange
    (255, 0, 0),  # Red
]

# Static circle segments with collision handling
def create_circle_boundary(radius, center):
    segments = []
    for i in range(36):
        angle1 = math.radians(i * 10)
        angle2 = math.radians((i + 1) * 10)

        start = (
            center[0] + radius * math.cos(angle1),
            center[1] + radius * math.sin(angle1),
        )
        end = (
            center[0] + radius * math.cos(angle2),
            center[1] + radius * math.sin(angle2),
        )

        segment = pymunk.Segment(space.static_body, start, end, 5)
        segment.elasticity = 1
        segment.friction = 0
        segment.collision_type = 1
        space.add(segment)
        segments.append(segment)
    return segments


class ColoredBall:
    def __init__(self, body, color, radius):
        self.body = body
        self.color = color
        self.radius = radius


color_count = 0


def create_ball(position):
    global color_count
    rr = radius + balls * 1.3
    mass = 1
    moment = pymunk.moment_for_circle(mass, 0, rr)
    body = pymunk.Body(mass, moment)
    body.position = position
    shape = pymunk.Circle(body, rr)
    shape.elasticity = 1
    shape.friction = 0
    shape.collision_type = 2
    space.add(body, shape)

    color = VIBGYOR_COLORS[color_count]
    color_count = (color_count + 1) % len(VIBGYOR_COLORS)
    return ColoredBall(body, color, rr)


balls = 1
colored_balls = []

# radius = ball size
radius = 10


# Collision handler to create new ball and play sound
def collision_handler(arbiter, space, data):
    global balls
    # Play the click sound when the ball hits the outer shell
    click_sound.play()
    
    if random.uniform(0, 1) < 1 / balls:
        new_ball = create_ball(circle_center)
        colored_balls.append(new_ball)
        balls += 1
    return True


# Create boundary and initial ball
circle_segments = create_circle_boundary(circle_radius, circle_center)
initial_ball = create_ball((circle_center[0] - 50, circle_center[1] - 50))
colored_balls.append(initial_ball)

# Set up collision handler
handler = space.add_collision_handler(1, 2)
handler.begin = collision_handler


# Custom drawing function
def draw_colored_balls():
    for ball in colored_balls:
        pos = ball.body.position
        pygame.draw.circle(screen, ball.color, (int(pos.x), int(pos.y)), ball.radius)


# Mouse repulsion parameters
REPULSION_RADIUS = 100
REPULSION_STRENGTH = 1000

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            # space.gravity = (0, -980)
            space.gravity = (0, -space.gravity[1])

    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Apply mouse repulsion
    for ball in colored_balls:
        # Calculate distance between ball and mouse
        dx = ball.body.position.x - mouse_pos[0]
        dy = ball.body.position.y - mouse_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        # Apply repulsion force if mouse is close
        if distance < REPULSION_RADIUS:
            # Normalize direction vector
            if distance > 0:
                force_x = dx / distance * REPULSION_STRENGTH
                force_y = dy / distance * REPULSION_STRENGTH
                ball.body.apply_force_at_local_point((force_x, force_y), (0, 0))

    # Clear screen with black background
    screen.fill((0, 0, 0))

    # Draw circle boundary in white
    pygame.draw.circle(screen, (255, 255, 255), circle_center, circle_radius, 10)

    # Draw colored balls
    draw_colored_balls()

    # Update physics
    space.step(1 / 60.0)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
