/*
- mock-twitter-api/main.go
This file sets up a mock HTTP server that simulates the X API v2 filtered stream endpoint.
It reads tweets from a local CSV file and streams them as JSON objects.
*/

package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strings"
	"time"

	// External libraries
	"github.com/joho/godotenv"
)

// Tweet represents the structure of a single tweet object that we will stream.
// This mimics the 'data' object in a real X API v2 stream response.
type Tweet struct {
	ID        string    `json:"id"`
	Text      string    `json:"text"`
	CreatedAt time.Time `json:"created_at"`
	AuthorID  string    `json:"author_id"` // The CSV does not have this field, so we will set it to a default value.
	Username  string    `json:"username"`
}

const defaultAuthorID = "123456789"
const defaultUsername = "mock_user"

// StreamResponse is the top-level object that wraps our Tweet data.
// The real X API response has this structure.
type StreamResponse struct {
	Data Tweet `json:"data"`
}

// csvFilePath is the path to the data source.
// We will use the tweets from the Kaggle Competition Dataset
// (https://www.kaggle.com/competitions/nlp-getting-started/overview)
const csvFilePath = "dataset/kaggle_test.csv"

// Define the rate lowerbound of the Tweet stream.
const streamRateLB = 2 * time.Second     // 2 seconds between tweets
const streamRateRandom = 2 * time.Second // Randomness in the stream rate

// main is the entry point for our mock API server.
func main() {
	// Define the handler for our mock streaming endpoint. Same endpoint as the real
	// X API v2 filtered stream, except for the base URL
	http.HandleFunc("/2/tweets/search/stream", streamTweetsHandler)

	// Load environment variables and define the port for the mock API server.
	godotenv.Load(".env") // Load the Environment Variables from the .env file
	port := os.Getenv("MOCK_API_PORT")
	if port == "" {
		log.Fatalf("MOCK_API_PORT is not set in the environment variables. Please set it in the .env file.")
	}

	// ======  Set the working directory to the directory of this file ====== 
	// This is necessary to ensure the CSV file can be found relative to this file's location
	if wd, err := os.Getwd(); err != nil {
		// If we cannot get the current working directory, log the error and exit.
		log.Fatalf("Failed to get current working directory: %v", err)
	} else if !strings.Contains(wd, "/mock_x_api") {
		// If not at the desired directory, change the working directory to the mock_x_api directory
		if err := os.Chdir("./src/mock_x_api/"); err != nil {
			log.Fatalf("Failed to change working directory: %v", err)
		}
	} 

	// Start the HTTP server.
	log.Printf("Starting Mock X API server on :%s", port)
	log.Println("Streaming endpoint available at http://localhost:8080/2/tweets/search/stream")
	log.Printf("Reading tweets from: %s", csvFilePath)

	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

// streamTweetsHandler handles the logic for streaming tweets to the client.
func streamTweetsHandler(w http.ResponseWriter, r *http.Request) {
	// Set the appropriate headers for a streaming JSON response.
	w.Header().Set("Content-Type", "application/json") // Set the content type to JSON.
	w.Header().Set("Transfer-Encoding", "chunked")     // Enable chunked transfer encoding for streaming.

	// Get a flusher to send data to the client in real-time.
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming not supported!", http.StatusInternalServerError)
		return
	}

	// Open the CSV file.
	file, err := os.Open(csvFilePath)
	if err != nil {
		log.Printf("Error opening CSV file: %v from path: %s", err, csvFilePath)
		http.Error(w, "Could not read tweet data source.", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	// Create a new CSV reader.
	reader := csv.NewReader(file)
	// Assuming the CSV has a header row, we read it once to skip it.
	if _, err := reader.Read(); err != nil {
		log.Printf("Error reading CSV header: %v", err)
		http.Error(w, "Failed to parse tweet data source.", http.StatusInternalServerError)
		return
	}

	// Get the request context to detect if the client has disconnected.
	ctx := r.Context()

	// Loop indefinitely to simulate a continuous stream.
	for {
		// Check if the client has disconnected
		select {
		case <-ctx.Done():
			// Client has disconnected, so we stop streaming.
			log.Println("Client disconnected. Closing stream.")
			return
		default:
			// Read one record (row) from the CSV file.
			record, err := reader.Read()
			if err != nil {
				// If we reach the end of the file, reset the reader to the beginning to loop the data.
				file.Seek(0, 0)
				reader = csv.NewReader(file)
				reader.Read() // Skip header again
				log.Println("Reached end of tweet file, looping back to the beginning.")
				continue
			}

			// Assuming CSV structure: id, keyword, location, text
			// We only need 'id' (index 0) and 'text' (index 3) from the CSV. The remaining fields can be set to default values.
			if len(record) < 4 {
				// Log an error if the record is malformed.
				log.Printf("Malformed record: %s", record)
				continue // Skip malformed rows
			}

			// Create a new tweet object.
			tweet := StreamResponse{
				Data: Tweet{
					ID:        record[0],
					Text:      record[3],
					CreatedAt: time.Now().UTC(), // Use the current time for CreatedAt
					AuthorID:  defaultAuthorID,  // Set to a default value
					Username:  defaultUsername,  // Set to a default value
				},
			}

			// Marshal the tweet object into a JSON byte array -- encode the Struct to JSON.
			jsonBytes, err := json.Marshal(tweet)
			if err != nil {
				log.Printf("Error marshaling tweet to JSON: %v", err)
				continue
			}

			// Write the JSON data to the response writer, followed by a newline.
			// The newline is required by the streaming API format to separate messages.
			// This is similar to how the real X API v2 stream sends data.
			fmt.Fprintf(w, "%s\n", jsonBytes)

			// Flush the data to the client to ensure it's sent immediately.
			flusher.Flush()

			// Wait for a short period to simulate a real-time feed.
			// This server dictates the rate of the stream since the Client will be actively
			// listening for new data (similar to how the real-time detection of tweets works).
			var delayTime = streamRateLB + time.Duration(rand.Int63n(int64(streamRateRandom)))

			time.Sleep(delayTime) // Sleep for a random duration to simulate real-time streaming.
		}
	}
}
