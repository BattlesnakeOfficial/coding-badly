import os
import time

import cherrypy

import pathfinding as pathfinding
import targeting as targeting


class Battlesnake:
    ENABLE_SERVER_LOGS = True

    def __init__(self):
        self.apiversion = "1"
        self.author = "bvanvugt"
        self.version = "v2"
        self.color = "#E80978"
        self.head = "shades"
        self.tail = "bolt"

    def run(self):
        if not self.ENABLE_SERVER_LOGS:
            cherrypy.log.screen = None

        cherrypy.config.update({"server.socket_host": "0.0.0.0"})
        cherrypy.config.update(
            {
                "server.socket_port": int(os.environ.get("PORT", "8080")),
            }
        )

        print("Starting Battlesnake Server...")
        server = Server()
        cherrypy.quickstart(server)

    def move(self, request):
        # turn = request["turn"]
        # print(f"\n{turn}")

        move = None
        possible_moves = pathfinding.calc_possible_moves(request)

        if possible_moves:
            if len(possible_moves) == 1:
                move = possible_moves[0]
            else:
                current_coords = request["you"]["head"]
                targets = targeting.calc_targets(request)
                for target_coords in targets:
                    move = pathfinding.calc_next_move(
                        request, current_coords, target_coords
                    )
                    if move:
                        # print(f"TARGETING -> {target_coords}")
                        break

        # print(f"{turn}: {possible_moves} -> {move}")
        return move


class Server(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        snake = Battlesnake()
        return {
            "apiversion": snake.apiversion,
            "author": snake.author,
            "version": snake.version,
            "color": snake.color,
            "head": snake.head,
            "tail": snake.tail,
        }

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def start(self):
        print("START")
        return "ok"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        data = cherrypy.request.json
        move = Battlesnake().move(data)
        if move is None:
            time.sleep(1)
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        print("END")
        return "ok"


if __name__ == "__main__":
    Battlesnake().run()
