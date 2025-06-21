import pygame
import time
import threading
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, KeyCode

pygame.init()

# global values
sliderMin = 1
sliderMax = 900
sliderX = 20
sliderY = 100
sliderWidth = 160
sliderHeight = 6
knobRadius = 6
font = pygame.font.SysFont(None, 24)

# Shared state
actualCPS = 10
clicking = False
mouse = Controller()
toggle = KeyCode(char="t")

# Lock for thread-safe CPS reading
cpsLock = threading.Lock()

def clicker():
    global actualCPS, clicking
    while True:
        if clicking:
            mouse.click(Button.left, 1)
            # Read CPS safely
            with cpsLock:
                delay = 1.0 / actualCPS
            time.sleep(delay)
        else:
            time.sleep(0.01)  # Sleep a bit when not clicking to save CPU

def toggleE(key):
    global clicking
    if key == toggle:
        clicking = not clicking

def startListener():
    clickThread = threading.Thread(target=clicker, daemon=True)
    clickThread.start()
    with Listener(on_press=toggleE) as listener:
        listener.join()

def drawSlider(win, cps):
    win.fill((30, 30, 30))

    # Draw slider bar
    pygame.draw.rect(win, (100, 100, 100), (sliderX, sliderY, sliderWidth, sliderHeight))

    # Knob position
    pos = sliderX + ((cps - sliderMin) / (sliderMax - sliderMin)) * sliderWidth

    # Draw knob
    pygame.draw.circle(win, (0, 200, 0), (int(pos), sliderY + sliderHeight // 2), knobRadius)

    # Draw CPS text
    txt = font.render(f"CPS: {int(cps)}", True, (255, 255, 255))
    txt2 = font.render(f"Turtle's auto clicker",True,(0,180,40))
    win.blit(txt2,(0,0))
    win.blit(txt, (60, 40))

def getCPSFromMouse(x):
    x = max(sliderX, min(sliderX + sliderWidth, x))
    percent = (x - sliderX) / sliderWidth
    return int(sliderMin + percent * (sliderMax - sliderMin))

def main():
    icon_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    icon_surface.fill((0, 0, 0, 0))
    pygame.display.set_icon(icon_surface)

    global actualCPS
    window = pygame.display.set_mode((200, 200))
    clock = pygame.time.Clock()
    pygame.display.set_caption(" ")
    run = True
    drag = False

    # Start listener thread (with clicker inside)
    listenerThread = threading.Thread(target=startListener, daemon=True)
    listenerThread.start()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if sliderY - 10 <= my <= sliderY + 20:
                    drag = True

            elif event.type == pygame.MOUSEBUTTONUP:
                drag = False

            elif event.type == pygame.MOUSEMOTION and drag:
                mx, my = pygame.mouse.get_pos()
                newCPS = getCPSFromMouse(mx)
                # Update actualCPS thread-safely
                with cpsLock:
                    actualCPS = newCPS

        # Draw slider and update display
        with cpsLock:
            currentCPS = actualCPS
        drawSlider(window, currentCPS)
        pygame.display.update()
        clock.tick(60)

main()
