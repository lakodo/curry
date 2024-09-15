class ProducerAlreadyRegistered(Exception):
    """
    Exception raised when a producer for a given format is already registered.

    Args:
        format_name (str): The name of the format.

    """

    def __init__(self, format_name: str):
        self.format_name = format_name
        self.message = f"Producer for {format_name} already exists"
        super().__init__(self.message)
