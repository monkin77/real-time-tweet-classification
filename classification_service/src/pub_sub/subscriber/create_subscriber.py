from .subscriber import Subscriber
from .redis_sub import RedisSub
from .kafka_sub import KafkaSub

def create_subscriber(subscriber_type: str, base_url: str, port: int, topic: str) -> Subscriber:
    '''
    Factory Design Pattern for creating a Subscriber instance.

    Given a Subscriber type and bootstrap servers, create an instance of the appropriate Subscriber.
    :param Subscriber_type: Type of the Subscriber (e.g., "kafka", "redis").
    :param bootstrap_servers: The address(es) of the message broker(s).

    :return: An instance of the Subscriber subclass corresponding to the Subscriber type.
    '''
    print(f"Initializing Subscriber of type: {subscriber_type} listening on topic: {topic} at {base_url}:{port}")

    if subscriber_type == "kafka":
        return KafkaSub(base_url=base_url, port=port, topic=topic)
    elif subscriber_type == "redis":
        return RedisSub(base_url=base_url, port=port, topic=topic)
    else:
        raise ValueError(f"Unsupported publisher type: {subscriber_type}")