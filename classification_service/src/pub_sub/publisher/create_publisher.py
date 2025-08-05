from publisher import Publisher
from kafka_pub import KafkaPub
# from redis_pub import RedisPub

def create_publisher(publisher_type: str, bootstrap_servers: str | list[str]) -> Publisher:
    '''
    Factory Design Pattern for creating a Publisher instance.

    Given a publisher type and bootstrap servers, create an instance of the appropriate publisher.
    :param publisher_type: Type of the publisher (e.g., "kafka", "redis").
    :param bootstrap_servers: The address(es) of the message broker(s).

    :return: An instance of the Publisher subclass corresponding to the publisher type.
    '''
    print(f"Initializing publisher of type: {publisher_type} with servers: {bootstrap_servers}")

    if publisher_type == "kafka":
        return KafkaPub(bootstrap_servers=bootstrap_servers)
    elif publisher_type == "redis":
        # return RedisPub(bootstrap_servers=bootstrap_servers)
        pass
    else:
        raise ValueError(f"Unsupported publisher type: {publisher_type}")