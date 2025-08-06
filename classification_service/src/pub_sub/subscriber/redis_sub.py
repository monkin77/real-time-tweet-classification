from .subscriber import Subscriber
import redis

class RedisSub(Subscriber):
    '''
    Redis Consumer class.
    '''
    def __init__(self, bootstrap_servers: str | list[str], topic: str):
        '''
        Initializes the Redis consumer.
        :param bootstrap_servers: The address(es) of the Redis server(s).
        '''
        super().__init__(consumer_type="redis", bootstrap_servers=bootstrap_servers, topic=topic)

        self.sub_client = redis.from_url(self.bootstrap_servers)

        # Initialize the Redis PubSub client
        self.pubsub = self.sub_client.pubsub()
       
    async def consume(self):
        """
        Consumes messages from a Redis Pub/Sub channel.
        This is an async generator that yields messages as they arrive.
        """
        if not self.pubsub:
            raise RuntimeError("Redis pubsub is not initialized. Call start() first.")
        
        await self.pubsub.subscribe(self.topic)
        print(f"Redis consumer subscribed to channel '{self.topic}'. Waiting for messages...")
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    await self.process_message(message["data"])
        except Exception as e:
            print(f"Error during Redis consumption: {e}")
        finally:
            await self.sub_client.close() 

    async def process_message(self, message_data: bytes):
        """
        Processes a single message.
        """
        print(f"Received message: {message_data[:200]}...")
        # Implement your message processing logic here

    async def close(self):
        """
        Closes the Redis consumer connection.
        """
        if self.pubsub:
            await self.pubsub.close()
        if self.sub_client:
            await self.sub_client.close()
        print("Redis consumer closed.")