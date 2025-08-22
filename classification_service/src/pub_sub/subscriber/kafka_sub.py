from .subscriber import Subscriber
from kafka import KafkaConsumer

class KafkaSub(Subscriber):
    '''
    Kafka Consumer class.
    '''
    def __init__(self, base_url: str, port: int, topic: str, kafka_config: dict = None):
        '''
        Initializes the Kafka consumer.
        :param base_url: The address of the Kafka broker.
        :param port: The port of the Kafka broker.
        :param topic: The Kafka topic to subscribe to.
        :param kafka_config: Additional Kafka consumer configuration.
        '''
        super().__init__(consumer_type="kafka", base_url=base_url, port=port, topic=topic)

        # Create a Kafka consumer
        kafka_broker = f"{base_url}:{port}"
        kafka_config = kafka_config or {}
        self.sub_client = KafkaConsumer(
            topic,
            bootstrap_servers=[kafka_broker],
            **kafka_config
        )

    async def consume(self):
        '''
        Consumes messages from a Kafka topic.
        This is an async generator that yields messages as they arrive.
        '''
        if not self.sub_client:
            raise RuntimeError("Kafka consumer is not initialized.")
        
        print(f"Kafka consumer subscribed to topic '{self.topic}'. Waiting for messages...")

        try:
            for msg in self.sub_client:
                # Yield the message value for processing
                yield msg.value
        except Exception as e:
            print(f"Error during Kafka consumption: {e}")
        finally:
            self.sub_client.close()

    async def close(self):
        '''
        Closes the Kafka consumer connection.
        '''
        if self.sub_client:
            self.sub_client.close()
