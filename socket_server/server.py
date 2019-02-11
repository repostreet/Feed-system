import os
import asyncio
import websockets
from dotenv import load_dotenv

ROOT_PATH = os.path.abspath('')
ENV = os.path.join(ROOT_PATH, '.env')
load_dotenv(ENV)


class Server:
    """
    Socket server class.
    Responsible for sending the real time update
    to web browser.
    """

    def __init__(self):
        """
        The 'connected' attribute of the socket server instance
        stores all the currently connected clients.
        """
        self.connected = set()

    def get_port(self):
        """
        To use custom port define a .env in te current dir and
        set env variable WS_PORT.
        """
        return os.getenv('WS_PORT', '8765')

    def get_host(self):
        """
        To use custom host define a .env in te current dir and
        set env variable WS_HOST.
        """
        return os.getenv('WS_HOST', 'localhost')

    def start(self):
        """Initialte the server."""
        return websockets.serve(self.handler, self.get_host(), self.get_port())

    async def handler(self, websocket, path):
        """
        Register new client connection
        and sends message to browser.
        """
        self.connected.add(websocket)

        # send message to clients
        async for message in websocket:
            print(message)
            await asyncio.wait([ws.send(message) for ws in self.connected])


if __name__ == '__main__':
    """
    Create the server instance and call the start method to
    start the server.
    """
    ws = Server()
    asyncio.get_event_loop().run_until_complete(ws.start())
    asyncio.get_event_loop().run_forever()
