from .publisher import Publisher
from .kafka_pub import KafkaPub
from .redis_pub import RedisPub

def create_publisher(publisher_type: str, base_url: str, port: int) -> Publisher:
    '''
    Factory Design Pattern for creating a Publisher instance.

    Given a publisher type and bootstrap servers, create an instance of the appropriate publisher.
    :param publisher_type: Type of the publisher (e.g., "kafka", "redis").
    :param bootstrap_servers: The address(es) of the message broker(s).

    :return: An instance of the Publisher subclass corresponding to the publisher type.
    '''
    print(f"Initializing publisher of type: {publisher_type} with servers: {base_url}:{port}")

    if publisher_type == "kafka":
        # return KafkaPub(bootstrap_servers=bootstrap_servers)
        pass
    elif publisher_type == "redis":
        return RedisPub(base_url=base_url, port=port)
    else:
        raise ValueError(f"Unsupported publisher type: {publisher_type}")