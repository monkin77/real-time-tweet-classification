package main

import (
	"log"

	// External libraries
	"github.com/joho/godotenv"

	// Project' Packages
	"github.com/monkin77/ingestion_service/src/client"
	"github.com/monkin77/ingestion_service/src/config"
)

func main() {
	// Load environment variables and define the API URL based on the DEV_MOCK_STREAM flag.
	godotenv.Load(".env") // Load the Environment Variables from the .env file
	cfg, err := config.LoadConfig(true)	// Load configuration for the client mode
	if err != nil {
		log.Fatalf("Error loading configuration: %v", err)
	}

	// Run the Client
	client.Client(cfg)
}