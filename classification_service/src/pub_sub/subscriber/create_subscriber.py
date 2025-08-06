from .subscriber import Subscriber
from .redis_sub import RedisSub

def create_subscriber(subscriber_type: str, bootstrap_servers: str | list[str], topic: str) -> Subscriber:
    '''
    Factory Design Pattern for creating a Subscriber instance.

    Given a Subscriber type and bootstrap servers, create an instance of the appropriate Subscriber.
    :param Subscriber_type: Type of the Subscriber (e.g., "kafka", "redis").
    :param bootstrap_servers: The address(es) of the message broker(s).

    :return: An instance of the Subscriber subclass corresponding to the Subscriber type.
    '''
    print(f"Initializing Subscriber of type: {subscriber_type} with servers: {bootstrap_servers}")

    if subscriber_type == "kafka":
        pass
        # return KafkaPub(bootstrap_servers=bootstrap_servers)
    elif subscriber_type == "redis":
        return RedisSub(bootstrap_servers=bootstrap_servers, topic=topic)
    else:
        raise ValueError(f"Unsupported publisher type: {subscriber_type}")