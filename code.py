import board
from adafruit_ht16k33.segments import BigSeg7x4
import wifi
import socketpool
from adafruit_httpserver import Server, Request, Response, POST, GET


i2c = board.I2C()
display = BigSeg7x4(i2c, address=0x70)
display.brightness = 0.2

pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, debug=True)


#  prints MAC address to REPL
# print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

#  prints IP address to REPL
# print("My IP address is", wifi.radio.ipv4_address)


FORM_HTML_TEMPLATE = """
<html lang="en">
    <head>
        <title>Update LEDs</title>
    </head>
    <body>
        <h2>Type in current total time (integers only).</h2>
        <form action="/" method="post" enctype="text/plain">
            <input type="text" name="TotalTime" placeholder="xxxx">
            <input type="submit" value="Submit">
        </form>
        {submitted_value}
    </body>
</html>
"""


@server.route("/", [GET, POST])
def form(request: Request):
    """
    Serve a form with the given enctype, and display back the submitted value.
    """
    enctype = request.query_params.get("enctype", "text/plain")

    if request.method == POST:
        posted_value = request.form_data.get("TotalTime")
        display.fill(0)
        display.print(posted_value)

    return Response(
        request,
        FORM_HTML_TEMPLATE.format(
            enctype=enctype,
            submitted_value=(
                f"<h3>Submitted form value: {posted_value}</h3>"
                if request.method == POST
                else ""
            ),
        ),
        content_type="text/html",
    )

server.serve_forever(str(wifi.radio.ipv4_address))
