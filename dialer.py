# dialer
import logging
import time
from LibraryX.Extra import VoIP

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] - %(message)s (%(name)s / %(funcName)s:%(lineno)d)',
)

voip = VoIP.VoIP('127.0.0.1')
voip.setup()

# try dail
voip.dial('127.0.0.1', 8277)

# wait for call 60 seconds
time.sleep(60)

voip.hangup()
