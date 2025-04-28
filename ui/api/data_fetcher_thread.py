from PySide6.QtCore import Qt, QThread, Signal

class DataFetcherThread(QThread):
    data_fetched = Signal(object)
    error_occurred = Signal(str)

    def __init__(self, api_client, api_url, params):
        super().__init__()
        self.api_client = api_client
        self.api_url = api_url
        self.params = params

    def run(self):
        try:
            if(self.api_url == "get-pickings"):
                resp = self.api_client.get_pickings(self.params)
            elif(self.api_url == "do-shipping"):
                resp = self.api_client.do_shipping(self.params)

            if "err_msg" in resp:
                self.error_occurred.emit(resp["err_msg"])
                return
            self.data_fetched.emit(resp)
        except Exception as e:
            self.error_occurred.emit(str(e))
