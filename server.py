import RNS
import RNS.vendor.umsgpack as msgpack
from pathlib import Path
import time


class server:
    def __init__(
        self,
        name=None,
        title=None,
        hls=None,
        filespath="./files",
        configpath="./config",
    ):
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

        self.app_data = {}
        if name is not None:
            self.app_data["name"] = name
        if title is not None:
            self.app_data["title"] = title
        if hls is not None:
            self.app_data["hls"] = hls
        if self.app_data != {}:
            self.destination.set_default_app_data(msgpack.packb(self.app_data))

        self.announce_interval = 20
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

    def announce(self):
        self.destination.announce()
        RNS.log("Sent announce from " + RNS.prettyhexrep(self.destination.hash))
        RNS.log(f"Active links: {len(self.destination.links)}")

    def server_loop(self):
        while True:
            self.announce()
            time.sleep(self.announce_interval * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="rns live streaming")
    parser.add_argument("--name")
    parser.add_argument("--title")
    parser.add_argument("--hls", help="your .m3u8 file in the /files")
    parser.add_argument("--files", default="./files")
    parser.add_argument("--config", default="./config")

    args = parser.parse_args()

    server = server(
        name=args.name,
        title=args.title,
        hls=args.hls,
        filespath=args.files,
        configpath=args.config,
    )
