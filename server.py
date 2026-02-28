import RNS
from pathlib import Path


class server:
    def __init__(self, filespath="./files", configpath="./config"):
        self.filespath = Path(filespath)
        self.configpath = Path(configpath)
        self.identitypath = self.configpath.joinpath("/identity")
        self.filespath.mkdir(parents=True, exist_ok=True)
        self.configpath.mkdir(parents=True, exist_ok=True)

        RNS.Reticulum()

        if self.identitypath.is_file():
            self.identity = RNS.Identity.from_file(self.identitypath)
            RNS.log("Loaded identity from file", RNS.LOG_INFO)
        else:
            RNS.log("No Primary Identity file found, creating new...", RNS.LOG_INFO)
            self.identity = RNS.Identity()
            self.identity.to_file(self.identitypath)

        self.destination = RNS.Destination(
            self.identity,
            RNS.Destination.IN,
            RNS.Destination.SINGLE,
            "live",
            "stream",
        )
        self.destination.register_request_handler(
            "/files",
            response_generator=self.files_generator,
            allow=RNS.Destination.ALLOW_ALL,
        )
        self.destination.set_link_established_callback(self.client_connected)
        RNS.log(f"Address: {RNS.prettyhexrep(self.destination.hash)}", RNS.LOG_INFO)

        self.server_loop()

    def client_connected(self, link: RNS.Link):
        pass

    def files_generator(
        self, path, data, request_id, link_id, remote_identity, requested_at
    ):
        try:
            filename = data.decode("utf-8")
            with open(self.filespath.joinpath(filename), "rb") as data_file:
                content = data_file.read()
                return content
        except Exception as e:
            RNS.log(
                f"Error while generating response to request {RNS.prettyhexrep(request_id)} on link {RNS.prettyhexrep(link_id)}, {e}",
                RNS.LOG_ERROR,
            )
            return b""

    def server_loop(self):
        RNS.log("Hit enter to manually send an announce (Ctrl-C to quit)")
        while True:
            entered = input()
            self.destination.announce()
            RNS.log("Sent announce from " + RNS.prettyhexrep(self.destination.hash))


if __name__ == "__main__":
    server()
