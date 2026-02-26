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
    server_destination.register_request_handler(
        "/files", response_generator=files_generator, allow=RNS.Destination.ALLOW_ALL
    )
    server_destination.set_link_established_callback(client_connected)
    RNS.log(f"Address: {RNS.prettyhexrep(server_destination.hash)}", RNS.LOG_INFO)

    server_loop(server_destination)


def client_connected(link: RNS.Link):
    pass


def files_generator(path, data, request_id, link_id, remote_identity, requested_at):
    try:
        filename = data.decode("utf-8")
        with open(serve_path.joinpath(filename), "rb") as data_file:
            content = data_file.read()
            return content
    except Exception as e:
        RNS.log(
            f"Error while generating response to request {RNS.prettyhexrep(request_id)} on link {RNS.prettyhexrep(link_id)}, {e}",
            RNS.LOG_ERROR,
        )
        return b""


def server_loop(destination):
    RNS.log("Hit enter to manually send an announce (Ctrl-C to quit)")
    while True:
        entered = input()
        destination.announce()
        RNS.log("Sent announce from " + RNS.prettyhexrep(destination.hash))


if __name__ == "__main__":
    main()
