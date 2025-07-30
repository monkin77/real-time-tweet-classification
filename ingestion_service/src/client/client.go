package client

import (
	"log"

	// Package Dependencies
	"github.com/monkin77/ingestion_service/src/config"
	"github.com/monkin77/ingestion_service/src/publisher"
)

// External libraries
func Client(cfg *config.Config) {
	// Print an hello message
	println("Hello, Ingestion Service!")

	// Initialize the publisher based on the configuration.
	publisherInstance, err := publisher.NewPublisher(cfg)
	if err != nil {
		log.Fatalf("Error initializing publisher: %v", err)
	}
	defer publisherInstance.Close() // Ensure the publisher is closed when done
	log.Printf("Publisher initialized: %s", cfg.PublisherType)

	// Connect to the selected API (Twitter or Mock API) and start streaming tweets.
	err = StreamTweets(cfg, publisherInstance) // Replace nil with the actual publisher instance
	if err != nil {
		log.Fatalf("Error streaming tweets: %v", err)
	}
}
