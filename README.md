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
```
python .\server.py
```
and make sure your HLS files(.m3u8 and .ts) are in the `files` folder.

for example:
```
ffmpeg -i input.mp4 -hls_playlist_type 2 output.m3u8
```
### client:
```
python .\client.py
```
then visit http://127.0.0.1:8000/{your_server_destination}/files/{m3u8_file} via your player.

for example:
```
ffplay http://127.0.0.1:8000/{your_server_destination}/files/output.m3u8
```
## working principle
This project uses HLS as the streaming media protocol. The client is actually an HTTP gateway.
## reference
https://reticulum.network/manual/examples.html
https://github.com/markqvist/Reticulum/discussions/295
