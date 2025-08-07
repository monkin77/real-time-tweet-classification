from .publisher import Publisher
import redis.asyncio as redis

TIMEOUT = 10  # Wait time for message to be sent (seconds)

class RedisPub(Publisher):

    def __init__(self, base_url: str, port: int):
        '''
        Initializes the Redis publisher with the topic and bootstrap servers.
        :param bootstrap_servers: The address(es) of the Redis server(s).
        :param topic: The Redis channel to publish messages to.
        '''
        # Call the base class constructor
        super().__init__(publisher_type="redis", base_url=base_url, port=port)

        # Create a Redis client
        # Not using password?
        self.pub_client = redis.Redis(host=base_url, port=port)

    async def publish(self, topic: str, message: bytes):
        '''
        Publish a message to the Redis channel.
        :param topic: The Redis channel to publish the message to.
        :param message: The message to be published.

        :return: The result of the send operation.
        '''
        if not self.pub_client:
            raise RuntimeError("Redis publisher is not initialized.")
        
        # Publish the message to the specified channel
        num_subscribers = await self.pub_client.publish(topic, message)

        # Return the result of the publish operation
        return num_subscribers

