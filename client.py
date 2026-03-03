import RNS
import RNS.vendor.umsgpack as msgpack
import time
from fastapi import FastAPI, Response, HTTPException
import uvicorn


class client:
    def __init__(self):
        RNS.Reticulum()
        self.app = FastAPI()

        @self.app.get("/{destination_hexhash}/files/{file_path:path}")
        def read_file(destination_hexhash: str, file_path: str):
            link = self.get_link(destination_hexhash)
            file: RNS.RequestReceipt = link.request("/files", file_path.encode("utf-8"))
            while not file.concluded():
                time.sleep(0.1)
            return Response(file.get_response())

        self.links: dict[str, RNS.Link] = {}
        self.announces_dict = {}

        class AnnounceHandler:
            def __init__(self2):
                self2.aspect_filter = "live.stream"

            def received_announce(
                self2, destination_hash, announced_identity, app_data
            ):
                RNS.log(
                    "Received an announce from " + RNS.prettyhexrep(destination_hash)
                )
                destination_hash = RNS.prettyhexrep(destination_hash)[1:-1]
                if app_data is not None:
                    self.announces_dict[destination_hash] = msgpack.unpackb(app_data)
                else:
                    self.announces_dict[destination_hash] = {}

        announce_handler = AnnounceHandler()
        RNS.Transport.register_announce_handler(announce_handler)

        @self.app.get("/")
        def get_list():
            return self.announces_dict

        uvicorn.run(self.app)

    def get_link(self, destination_hexhash):
        """see https://reticulum.network/manual/examples.html"""
        if destination_hexhash not in self.links:
            dest_len = (RNS.Reticulum.TRUNCATED_HASHLENGTH // 8) * 2
            if len(destination_hexhash) != dest_len:
                raise ValueError(
                    "Destination length is invalid, must be {hex} hexadecimal characters ({byte} bytes).".format(
                        hex=dest_len, byte=dest_len // 2
                    )
                )
            destination_hash = bytes.fromhex(destination_hexhash)
            if not RNS.Transport.has_path(destination_hash):
                RNS.log(
                    "Destination is not yet known. Requesting path and waiting for announce to arrive..."
                )
                RNS.Transport.request_path(destination_hash)
                while not RNS.Transport.has_path(destination_hash):
                    time.sleep(0.1)
            server_identity = RNS.Identity.recall(destination_hash)
            RNS.log("Establishing link with server...")
            server_destination = RNS.Destination(
                server_identity,
                RNS.Destination.OUT,
                RNS.Destination.SINGLE,
                "live",
                "stream",
            )
            link = RNS.Link(server_destination)
            link.set_link_closed_callback(self.link_closed)
            self.links[destination_hexhash] = link
        while self.links[destination_hexhash].status != RNS.Link.ACTIVE:
            time.sleep(0.1)
        return self.links[destination_hexhash]

    def link_closed(self, link: RNS.Link):
        if link.teardown_reason == RNS.Link.TIMEOUT:
            RNS.log("The link timed out, exiting now")
        elif link.teardown_reason == RNS.Link.DESTINATION_CLOSED:
            RNS.log("The link was closed by the server, exiting now")
        else:
            RNS.log("Link closed, exiting now")
        self.links.pop(RNS.prettyhexrep(link.destination.hash)[1:-1])


if __name__ == "__main__":
    client()
