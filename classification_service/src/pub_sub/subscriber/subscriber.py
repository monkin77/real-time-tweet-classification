class Subscriber():
    '''
    Base class for all Consumers.
    This class provides a common interface for consuming messages from different systems.
    E.g. Kafka, Redis, etc.
    '''
    def __init__(self, consumer_type: str, base_url: str, port: int, topic: str):
        '''
        Initializes the Subscriber with the type and bootstrap servers.
        :param consumer_type: Type of the consumer (e.g., "kafka", "redis").
        :param bootstrap_servers: The address(es) of the message broker(s).
        :param topic: The topic to subscribe to.
        '''
        self.consumer_type = consumer_type
        self.base_url = base_url
        self.port = port
        self.topic = topic

        self.consumer = None  # This will be initialized in subclasses

    """ async def start(self):
        '''
        Start the consumer.
        This method should be overridden by subclasses to implement specific starting logic.
        '''
        raise NotImplementedError("Subclasses must implement this method.") """

    async def consume(self):
        """
        Consume messages from the specified topic.
        This method should be overridden by subclasses to implement specific consuming logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    
    async def process_message(message_data: bytes):
        '''
        Process a single message.
        This method should be overridden by subclasses to implement specific message processing logic.
        '''
        raise NotImplementedError("Subclasses must implement this method.")

    async def close(self):
        """
        Close the consumer connection.
        This method should be overridden by subclasses to implement specific closing logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")