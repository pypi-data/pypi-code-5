#!/usr/bin/env pypy
from __future__ import (print_function, division, absolute_import)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..'))
import traceback

from _sdl.internal import *

################################################################################

def poll_events():
    while True:
        event = SDL_PollEvent()
        if event:
            yield event
        else:
            return

def main(argv):
    try:
        assert SDL_Init(SDL_INIT_VIDEO | SDL_INIT_AUDIO) >= 0, 'Unable to initialize SDL'

        #SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3)
        #SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 2)

        SDL_GL_SetAttribute(SDL_GL_DOUBLEBUFFER, 1)
        SDL_GL_SetAttribute(SDL_GL_DEPTH_SIZE, 24)

        mainwindow = SDL_CreateWindow("SDL Test Window", SDL_WINDOWPOS_CENTERED,
            SDL_WINDOWPOS_CENTERED, 512, 512, SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN)
        assert mainwindow, "Unable to create main window"

        maincontext = SDL_GL_CreateContext(mainwindow)
        SDL_GL_SetSwapInterval(1)

        quit = False
        while not quit:
            for event in poll_events():
                if event.type == SDL_QUIT:
                    quit = True
                elif event.type == SDL_MOUSEMOTION:
                    print(event.motion.x, event.motion.y)
                elif event.type == SDL_MOUSEBUTTONDOWN:
                    if event.button.which == 0:
                        print("grabbing...")
                        SDL_SetRelativeMouseMode(True)
                elif event.type == SDL_MOUSEBUTTONUP:
                    if event.button.which == 0:
                        print("releasing...")
                        SDL_SetRelativeMouseMode(False)

            SDL_GL_SwapWindow(mainwindow)

        SDL_GL_DeleteContext(maincontext)
        SDL_DestroyWindow(mainwindow)

    except:
        traceback.print_exc()
    SDL_Quit()

if __name__ == '__main__':
    main(sys.argv)
