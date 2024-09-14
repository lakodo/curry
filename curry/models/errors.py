class ProducerAlreadyRegistered(Exception):
    def __init__(self, format_name: str):
        self.format_name = format_name
        self.message = f"Producer for {format_name} already exists"
        super().__init__(self.message)
