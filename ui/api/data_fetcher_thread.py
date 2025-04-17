from PySide6.QtCore import Qt, QThread, Signal

class DataFetcherThread(QThread):
    data_fetched = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, api_client, api_url, param):
        super().__init__()
        self.api_client = api_client
        self.api_url = api_url

    def run(self):
        try:
            if(self.api_url == "get-pickings"):
                resp = self.api_client.get_pickings()
            elif(self.api_url == "do-shipping"):
                resp = self.api_client.do_shipping()
            if "pickings" in resp:
                self.data_fetched.emit(resp["pickings"])
            else:
                self.data_fetched.emit([])
        except Exception as e:
            self.error_occurred.emit(str(e))
