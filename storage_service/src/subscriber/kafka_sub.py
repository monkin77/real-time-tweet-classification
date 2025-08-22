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

        tries = 0
        while tries < 3:
            try:
                self.consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=[kafka_broker],
                    **kafka_config
                )

                print(f"Kafka consumer initialized and connected to broker at {kafka_broker}, subscribed to topic '{topic}'.")
                break  # Exit the loop if successful
            except Exception as e:
                print(f"Error initializing Kafka consumer: {e}. Retrying...")
                
                # Wait for 3 seconds
                import time
                time.sleep(3)
                tries += 1  # Increment the tries counter

    async def consume(self):
        '''
        Consumes messages from a Kafka topic.
        This is an async generator that yields messages as they arrive.
        '''
        if not self.consumer:
            raise RuntimeError("Kafka consumer is not initialized.")
        
        print(f"Kafka consumer subscribed to topic '{self.topic}'. Waiting for messages...")

        try:
            for msg in self.consumer:
                # Yield the message value for processing
                yield msg.value
        except Exception as e:
            print(f"Error during Kafka consumption: {e}")
        finally:
            self.consumer.close()

    async def close(self):
        '''
        Closes the Kafka consumer connection.
        '''
        if self.consumer:
            self.consumer.close()
