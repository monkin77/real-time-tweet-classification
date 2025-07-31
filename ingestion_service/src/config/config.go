package config

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
	MockAPIHost           string
	DevMockStream         bool
	MockAPIPort           string
	DockerMode			  bool // Indicates if the service is running in Docker mode
}

// LoadConfig loads the configuration from environment variables.
// It checks for required variables and returns an error if any are missing or invalid.
// Parameters:
// - isClient: A boolean indicating if the configuration is being loaded for the client.
//   If true, it will require a different set of environment variables.
// Returns: Config object or an error if any required variable is missing or invalid.
func LoadConfig(isClient bool) (*Config, error) {
	var (
		twitterBearerToken    = os.Getenv("TWITTER_BEARER_TOKEN")
		publisherType         = os.Getenv("PUBLISHER_TYPE")
		redisAddr             = os.Getenv("REDIS_ADDR")
		redisPassword         = os.Getenv("REDIS_PASSWORD")
		redisChannel          = os.Getenv("REDIS_CHANNEL")
		kafkaBootstrapServers = os.Getenv("KAFKA_BOOTSTRAP_SERVERS")
		kafkaTopic            = os.Getenv("KAFKA_TOPIC")
		devMockStream         = os.Getenv("DEV_MOCK_STREAM")
		mockAPIHost           = os.Getenv("MOCK_API_HOST")
		mockAPIPort           = os.Getenv("MOCK_API_PORT")
		dockerMode			  = os.Getenv("DOCKER_MODE")
	)

	devMockStreamBool, dockerModeBool := true, true // Default to true for backward compatibility
	err := error(nil)	// Define err to capture any errors during parsing

	if isClient {
		// Check for required environment variables for the client.
		if twitterBearerToken == "" {
			return nil, fmt.Errorf("TWITTER_BEARER_TOKEN is not set")
		}

		devMockStreamBool, err = strconv.ParseBool(devMockStream)
		if err != nil {
			return nil, fmt.Errorf("failed to parse DEV_MOCK_STREAM: %w", err)
		}

		if devMockStreamBool && mockAPIHost == "" {
			// Default to localhost for backward compatibility with local non-docker runs.
			mockAPIHost = "localhost"
		}

		if publisherType != "redis" && publisherType != "kafka" {
			return nil, fmt.Errorf("invalid PUBLISHER_TYPE: %s, must be 'redis' or 'kafka'", publisherType)
		}
	} else {
		// Check for required environment variables for the mock API.
		if mockAPIPort == "" {
			return nil, fmt.Errorf("MOCK_API_PORT is not set in Server")
		}

		if mockAPIHost == "" {
			return nil, fmt.Errorf("MOCK_API_HOST is not set in Server")
		}
	}

	if dockerMode != "" {
		dockerModeBool, err = strconv.ParseBool(dockerMode)
		if err != nil {
			return nil, fmt.Errorf("failed to parse DOCKER_MODE: %w", err)
		}
	}


	cfg := &Config{
		TwitterBearerToken:    twitterBearerToken,
		PublisherType:         publisherType,
		RedisAddr:             redisAddr,
		RedisPassword:         redisPassword,
		RedisChannel:          redisChannel,
		KafkaBootstrapServers: kafkaBootstrapServers,
		KafkaTopic:            kafkaTopic,
		MockAPIHost:           mockAPIHost,
		DevMockStream:         devMockStreamBool,
		MockAPIPort:           mockAPIPort,
		DockerMode: 		   dockerModeBool,
	}

	return cfg, nil
}
