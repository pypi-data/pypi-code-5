"""Simple script to print out the (x,y,z) location of the current player on
a minecraft server


usage:  python playerloc.py [server-name] [port]


"""

import rube_mc_pi.mcpi.minecraft as minecraft
import sys
import time


if __name__ == "__main__":
    servername = "localhost"
    port = 25565
    if len(sys.argv) > 1:
        servername = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    print("Opening world '%s:%d'" % (servername, port))
    world = minecraft.Minecraft.create(servername, port)
    print("Connected to world")
    print world.player.getPos()
    print("Player is at (%d, %d, %d)" % world.player.getPos())
