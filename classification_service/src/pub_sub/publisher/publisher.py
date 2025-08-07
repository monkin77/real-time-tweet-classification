class Publisher:
    '''
    Base Class for all publishers.
    This class provides a common interface for publishing messages to different systems.
    E.g. Kafka, Redis, etc.
    '''
    def __init__(self, publisher_type: str, base_url: str, port: int):
        '''
        Initializes the Publisher with the type and bootstrap servers.
        :param publisher_type: Type of the publisher (e.g., "kafka", "redis").
        :param base_url: The address(es) of the message broker(s).
        :param port: The port number of the message broker.
        '''
        self.publisher_type = publisher_type
        self.base_url = base_url
        self.port = port

        self.producer = None    # This will be initialized in subclasses

    async def publish(self, topic: str, message: bytes):
        """
        Publish a message to the specified topic.
        This method should be overridden by subclasses to implement specific publishing logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    async def close(self):
        """
        Close the publisher connection.
        This method should be overridden by subclasses to implement specific closing logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")