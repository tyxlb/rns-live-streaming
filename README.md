# rns-live-streaming
live stream on rns!

Real-time protocols have explicit servers, which is much simpler than protocols that rely on offline assumptions.(maybe?)
## use case
* Live streaming, webcam, internet TV
* Video websites, music websites
* Media Library
* Your creativity
## usage
```
pip install -r .\requirements.txt
```
### server:
In the latest version, you should use [MediaMtx](https://github.com/bluenviron/mediamtx) in combination (or configure your own streaming media server).

Start MediaMtx (you can use the default configuration) and push a stream to rtmp://localhost/mystream (e.g., OBS). Then:
```
python .\server.py
```
By default, this will forward http://localhost:8888 and announce `mystream/index.m3u8`.

I suggest including the name, title, and .m3u8 file in the announcement, for example:
```
python .\server.py --name NAME --title TITLE --hls mystream/index.m3u8
```
### client:
```
python .\client.py
```
then visit http://127.0.0.1:8000/{your_server_destination}/files/{m3u8_file} via your player.

for example:
```
ffplay http://127.0.0.1:8000/{your_server_destination}/files/mystream/index.m3u8
```
You can also keep the client open and listen to announcements on the network. http://127.0.0.1:8000/ will return a dictionary containing known destinations (and .m3u8 files).
## working principle
This project uses HLS as the streaming media protocol. The client is actually an HTTP gateway.
## reference
https://reticulum.network/manual/examples.html

https://github.com/markqvist/Reticulum/discussions/295
