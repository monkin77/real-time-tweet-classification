package publisher

/*
import (
	"fmt"
	"log"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	"github.comcom/your-username/ingestion-service/internal/config"
)

// KafkaPublisher implements the Publisher interface for Apache Kafka.
type KafkaPublisher struct {
	producer *kafka.Producer
	topic    string
}

// NewKafkaPublisher creates a new publisher that sends messages to a Kafka topic.
func NewKafkaPublisher(cfg *config.Config) (*KafkaPublisher, error) {
	p, err := kafka.NewProducer(&kafka.ConfigMap{
		"bootstrap.servers": cfg.KafkaBootstrapServers,
	})

	if err != nil {
		return nil, fmt.Errorf("failed to create Kafka producer: %w", err)
	}

	log.Println("Successfully connected to Kafka.")

	// Go-routine to handle delivery reports from Kafka.
	// This is important for understanding if messages are being delivered successfully.
	go func() {
		for e := range p.Events() {
			switch ev := e.(type) {
			case *kafka.Message:
				if ev.TopicPartition.Error != nil {
					log.Printf("Kafka delivery failed: %v\n", ev.TopicPartition)
				}
			}
		}
	}()

	return &KafkaPublisher{
		producer: p,
		topic:    cfg.KafkaTopic,
	}, nil
}

// Publish sends a message to the configured Kafka topic.
func (p *KafkaPublisher) Publish(message string) error {
	return p.producer.Produce(&kafka.Message{
		TopicPartition: kafka.TopicPartition{Topic: &p.topic, Partition: kafka.PartitionAny},
		Value:          []byte(message),
	}, nil)
}

// Close flushes and closes the Kafka producer.
func (p *KafkaPublisher) Close() {
	p.producer.Flush(15 * 1000) // Wait up to 15 seconds for all messages to be delivered.
	p.producer.Close()
}
*/
