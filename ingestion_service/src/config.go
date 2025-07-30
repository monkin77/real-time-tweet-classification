package main

import (
	"fmt"
	"os"
	"strconv"
)

// Config stores the application configuration.
type Config struct {
	TwitterBearerToken    string
	PublisherType         string
	RedisAddr             string
	RedisPassword         string
	RedisChannel          string
	KafkaBootstrapServers string
	KafkaTopic            string
	DevMockStream         bool
	MockAPIPort           string
}

// LoadConfig loads the configuration from environment variables.
// It checks for required variables and returns an error if any are missing or invalid.
// Returns: Config object or an error if any required variable is missing or invalid.
func LoadConfig() (*Config, error) {
	var (
		twitterBearerToken    = os.Getenv("TWITTER_BEARER_TOKEN")
		publisherType         = os.Getenv("PUBLISHER_TYPE")
		redisAddr             = os.Getenv("REDIS_ADDR")
		redisPassword         = os.Getenv("REDIS_PASSWORD")
		redisChannel          = os.Getenv("REDIS_CHANNEL")
		kafkaBootstrapServers = os.Getenv("KAFKA_BOOTSTRAP_SERVERS")
		kafkaTopic            = os.Getenv("KAFKA_TOPIC")
		devMockStream         = os.Getenv("DEV_MOCK_STREAM")
		mockAPIPort           = os.Getenv("MOCK_API_PORT")
	)

	if twitterBearerToken == "" {
		return nil, fmt.Errorf("TWITTER_BEARER_TOKEN is not set")
	}

	devMockStreamBool, err := strconv.ParseBool(devMockStream)
	if err != nil {
		return nil, fmt.Errorf("failed to parse DEV_MOCK_STREAM: %w", err)
	}

	if publisherType != "redis" && publisherType != "kafka" {
		return nil, fmt.Errorf("invalid PUBLISHER_TYPE: %s, must be 'redis' or 'kafka'", publisherType)
	}

	cfg := &Config{
		TwitterBearerToken:    twitterBearerToken,
		PublisherType:         publisherType,
		RedisAddr:             redisAddr,
		RedisPassword:         redisPassword,
		RedisChannel:          redisChannel,
		KafkaBootstrapServers: kafkaBootstrapServers,
		KafkaTopic:            kafkaTopic,
		DevMockStream:         devMockStreamBool,
		MockAPIPort:           mockAPIPort,
	}

	return cfg, nil
}
