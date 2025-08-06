from kafka import KafkaProducer
from .publisher import Publisher

TIMEOUT = 10  # Wait time for message to be sent (seconds)

class KafkaPub(Publisher):

    def __init__(self, bootstrap_servers: str | list[str]):
        '''
        Initializes the Kafka publisher with the topic and bootstrap servers.
        :param bootstrap_servers: The address(es) of the Kafka broker(s).
        :param topic: The Kafka topic to publish messages to.
        '''
        # Call the base class constructor
        super().__init__(publisher_type="kafka", bootstrap_servers=bootstrap_servers)

        # Initialize the Kafka producer
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

    async def publish(self, topic: str, message: bytes):
        '''
        Publish a message to the Kafka topic.
        :param message: The message to be published.
        :param topic: The Kafka topic to publish the message to.

        :return: The result of the send operation.
        '''
        if not self.producer:
            raise RuntimeError("Kafka producer is not initialized.")
        
        # Send the message to the specified topic
        future = self.producer.send(topic, value=message)  # Asynchronously send the message

        # Wait for the message to be sent (Block until the message is acknowledged)
        # This will raise an exception if the message could not be sent within the timeout
        # TODO: Should we block?
        result = future.get(timeout=TIMEOUT)  # Wait for the message to be sent

        # Return the result of the send operation
        return result

