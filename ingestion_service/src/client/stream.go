package client

import (
	"bufio"
	"fmt"
	"log"
	"net/http"

	// Package Dependencies
	"github.com/monkin77/ingestion_service/src/config"
	"github.com/monkin77/ingestion_service/src/publisher"
)

// StreamTweets connects to the Twitter API (or mock API) and streams tweets.
// TODO: Replace the `pub` parameter with the actual publisher interface that implements the Publish method.
func StreamTweets(cfg *config.Config, pub publisher.Publisher) error {
	var (
		resp    *http.Response
		err     error
		apiURL  string
		message string
	)

	if cfg.DevMockStream {
		// Use the Hostname and Port from the configuration for the mock API.
		apiURL = "http://" + cfg.MockAPIHost + ":" + cfg.MockAPIPort
		log.Printf("Using Mock API for development. URL: %s\n\n", apiURL)
	} else {
		apiURL = "https://api.x.com"
		log.Printf("Using Live API for production. URL: %s\n\n", apiURL)
	}

	// Create a new HTTP Client to send the request to the API.
	// This client will handle the connection to the API and read the stream.
	client := &http.Client{}

	// Make the HTTP Get Request to the streaming endpoint.
	streamEndpoint := apiURL + "/2/tweets/search/stream"
	req, err := http.NewRequest("GET", streamEndpoint, nil)
	if err != nil {
		return fmt.Errorf("error creating request to stream endpiont: %w", err)
	}

	// Add the bearer token to the request header -- Authorization header.
	req.Header.Add("Authorization", "Bearer "+cfg.TwitterBearerToken)

	// Send the request to the API.
	// The response will be a stream of tweets.
	resp, err = client.Do(req)

	if err != nil {
		return fmt.Errorf("error connecting to the API: %w", err)
	}
	// Ensure the response body is closed after reading.
	// This only runs once the encapsulating function (StreamTweets) returns.
	defer resp.Body.Close()

	// Check the response status code.
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("API returned an error: %s", resp.Status)
	}

	// Create a new scanner to read the response body line by line.
	// This allows us to process each tweet as it comes in.
	// The response body is a stream of tweets in JSON format.
	scanner := bufio.NewScanner(resp.Body)
	for scanner.Scan() {
		// Get the tweet text from the response.
		message = scanner.Text()

		// Publish the tweet to the message queue.
		err = pub.Publish(message)
		if err != nil {
			log.Printf("Error publishing message: %v", err)
			continue // Continue to the next tweet even if publishing fails
		}

		log.Printf("Tweet %s published successfully.", message)
	}

	// Check for errors during scanning.
	if err := scanner.Err(); err != nil {
		return fmt.Errorf("error reading stream: %w", err)
	}

	return nil
}
