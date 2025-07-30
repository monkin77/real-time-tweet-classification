package main

import (
	"log"

	"github.com/joho/godotenv"
)

// External libraries

func main() {
	// Print an hello message
	println("Hello, Ingestion Service!")

	// Load environment variables and define the API URL based on the DEV_MOCK_STREAM flag.
	godotenv.Load(".env") // Load the Environment Variables from the .env file
	cfg, err := LoadConfig()
	if err != nil {
		log.Fatalf("Error loading configuration: %v", err)
	}

	// Initialize the publisher based on the configuration.
	// TODO

	// Connect to the selected API (Twitter or Mock API) and start streaming tweets.
	err = StreamTweets(cfg, nil) // Replace nil with the actual publisher instance
	if err != nil {
		log.Fatalf("Error streaming tweets: %v", err)
	}
}
