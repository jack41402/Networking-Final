# receiver
import logging
import time
from LibraryX.Extra import VoIP

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] - %(message)s (%(name)s / %(funcName)s:%(lineno)d)',
)

voip = VoIP.VoIP('127.0.0.1')
voip.setup()

# check the debug message to get the ringtone server port

# this call will be auto accepted

# wait for call 60 seconds
time.sleep(60)

voip.hangup()
