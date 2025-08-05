class Publisher:
    '''
    Base Class for all publishers.
    This class provides a common interface for publishing messages to different systems.
    E.g. Kafka, Redis, etc.
    '''
    def __init__(self, publisher_type: str, bootstrap_servers: str | list[str]):
        '''
        Initializes the Publisher with the type and bootstrap servers.
        :param publisher_type: Type of the publisher (e.g., "kafka", "redis").
        :param bootstrap_servers: The address(es) of the message broker(s).
        '''
        self.publisher_type = publisher_type
        self.bootstrap_servers = bootstrap_servers

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