import time

from bleson import get_provider, Advertiser, Advertisement

adapter = get_provider().get_adapter()

advertiser = Advertiser(adapter)
advertisement = Advertisement()
advertisement.name = "RODAN"

advertiser.advertisement = advertisement

advertiser.start()
time.sleep(10)
advertiser.stop()
