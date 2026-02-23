import RNS
import time
from fastapi import FastAPI, Response, HTTPException
from contextlib import asynccontextmanager
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    reticulum = RNS.Reticulum()
    yield


app = FastAPI(lifespan=lifespan)

links: dict[str, RNS.Link] = {}
datas: dict[str, dict[str, Response | HTTPException]] = {}


def get_link(destination_hexhash):
    """see https://reticulum.network/manual/examples.html"""
    if destination_hexhash not in links:
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
        link.set_resource_strategy(RNS.Link.ACCEPT_ALL)
        link.set_resource_concluded_callback(download_concluded)
        link.set_link_closed_callback(link_closed)
        links[destination_hexhash] = link
        datas[str(link)] = {}
    while links[destination_hexhash].status != RNS.Link.ACTIVE:
        time.sleep(0.1)
    return links[destination_hexhash]


def link_closed(link: RNS.Link):
    links.pop(str(link)[1:-1])


@app.get("/{destination_hexhash}/files/{file_path:path}")
def read_file(destination_hexhash: str, file_path: str):
    link = get_link(destination_hexhash)
    datas[str(link)][file_path] = None
    request_packet = RNS.Packet(link, file_path.encode("utf-8"), create_receipt=False)
    request_packet.send()
    while datas[str(link)][file_path] is None:
        time.sleep(0.1)

    return datas[str(link)][file_path]


def download_concluded(resource: RNS.Resource):
    if resource.status == RNS.Resource.COMPLETE:
        datas[str(resource.link)][str(resource.metadata)] = Response(
            resource.data.read()
        )
    else:
        datas[str(resource.link)][str(resource.metadata)] = HTTPException(
            500, resource.status
        )


uvicorn.run(
    app,
)
