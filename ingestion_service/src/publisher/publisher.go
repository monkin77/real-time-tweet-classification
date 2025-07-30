package publisher

import (
	"fmt"

	"github.com/monkin77/ingestion_service/src/config"
)

// Publisher defines the interface for publishing messages to a message queue.
// This allows for different implementations (e.g., Redis, Kafka) to be used interchangeably.
type Publisher interface {
	Publish(message string) error
	Close()
}

// NewPublisher acts as a Factory, creating and returning the correct publisher
// instance based on the application's configuration.
func NewPublisher(cfg *config.Config) (Publisher, error) {
	// Create a Publisher based on the configuration.
	switch cfg.PublisherType {
	case "redis":
		return NewRedisPublisher(cfg)
	case "kafka":
		return nil, fmt.Errorf("TODO")
		// return NewKafkaPublisher(cfg)
	default:
		return nil, fmt.Errorf("unsupported publisher type: %s", cfg.PublisherType)
	}
}
