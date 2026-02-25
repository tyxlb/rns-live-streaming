import RNS
from pathlib import Path

serve_path = Path("./files")
configpath = Path("./config")
identitypath = configpath.joinpath("/identity")


def main():
    serve_path.mkdir(parents=True, exist_ok=True)
    configpath.mkdir(parents=True, exist_ok=True)

    reticulum = RNS.Reticulum()

    if identitypath.is_file():
        identity = RNS.Identity.from_file(identitypath)
        RNS.log("Loaded identity from file", RNS.LOG_INFO)
    else:
        RNS.log("No Primary Identity file found, creating new...", RNS.LOG_INFO)
        identity = RNS.Identity()
        identity.to_file(identitypath)

    server_destination = RNS.Destination(
        identity,
        RNS.Destination.IN,
        RNS.Destination.SINGLE,
        "live",
        "stream",
    )
    server_destination.set_link_established_callback(client_connected)
    RNS.log(f"Address: {RNS.prettyhexrep(server_destination.hash)}", RNS.LOG_INFO)

    server_loop(server_destination)


def client_connected(link: RNS.Link):
    link.set_packet_callback(client_request)


def client_request(message: bytes, packet):
    try:
        filename = message.decode("utf-8")
        with open(serve_path.joinpath(filename), "rb") as data_file:
            content = data_file.read()
            resource = RNS.Resource(content, packet.link, metadata=filename)
    except Exception as e:
        RNS.log('Error while reading file "' + filename + '"', RNS.LOG_ERROR)
        packet.link.teardown()
        raise e


def server_loop(destination):
    RNS.log("Hit enter to manually send an announce (Ctrl-C to quit)")
    while True:
        entered = input()
        destination.announce()
        RNS.log("Sent announce from " + RNS.prettyhexrep(destination.hash))


if __name__ == "__main__":
    main()
