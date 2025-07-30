package publisher

import (
	"context"
	"fmt"
	"log"

	// External libraries
	"github.com/redis/go-redis/v9"

	// Project's Packages
	"github.com/monkin77/ingestion_service/src/config"
)

// RedisPublisher implements the Publisher interface for Redis Pub/Sub.
type RedisPublisher struct {
	client  *redis.Client
	channel string
	ctx     context.Context
}

// NewRedisPublisher creates a new publisher that sends messages to a Redis channel.
// Parameters:
// - cfg: Configuration containing Redis connection details.
// Returns:
// - A pointer to RedisPublisher or an error if the connection fails.
func NewRedisPublisher(cfg *config.Config) (*RedisPublisher, error) {
	client := redis.NewClient(&redis.Options{
		Addr:     cfg.RedisAddr,
		Password: cfg.RedisPassword,
		DB:       0, // use default DB
	})

	ctx := context.Background() // Create a context for Redis operations

	// Ping the Redis server to ensure a connection can be established.
	if _, err := client.Ping(ctx).Result(); err != nil {
		return nil, fmt.Errorf("failed to connect to Redis: %w", err)
	}

	log.Println("Successfully connected to Redis.")
	return &RedisPublisher{
		client:  client,
		channel: cfg.RedisChannel,
		ctx:     ctx,
	}, nil
}

// Publish sends a message to the configured Redis channel.
// Parameters:
// - message: The message to be published.
// Returns:
// - An error if the publish operation fails.
func (p *RedisPublisher) Publish(message string) error {
	return p.client.Publish(p.ctx, p.channel, message).Err()
}

// Close closes the Redis client connection.
func (p *RedisPublisher) Close() {
	p.client.Close()
}
