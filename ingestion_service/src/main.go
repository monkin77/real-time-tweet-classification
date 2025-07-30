package main

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

// External libraries

func main() {
	// Print an hello message
	println("Hello, Ingestion Service!")

	// Load environment variables and define the API URL based on the DEV_MOCK_STREAM flag.
	godotenv.Load(".env") // Load the Environment Variables from the .env file
	USE_MOCK_API := os.Getenv("DEV_MOCK_STREAM") == "true"
	API_URL := "https://api.x.com"
	if USE_MOCK_API {
		port := os.Getenv("MOCK_API_PORT")
		if port == "" {
			log.Fatalf("MOCK_API_PORT is not set in the environment variables. Please set it in the .env file.")
		}
		API_URL = "http://localhost:" + port
		log.Printf("Using Mock API for development. URL: %s\n", API_URL)
	} else {
		log.Printf("Using Live API for production. URL: %s\n", API_URL)
	}

	
}
