package main

import (
	"fmt"
	"net/http"
)

func main() {
	// Print an hello message
	println("Hello, Ingestion Service!")

	// Initialize the X API Client (inline for now)
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// Print the requested path
		fmt.Fprintf(w, "Hello, you've requested %s\n", r.URL.Path)
	})

	// Start the HTTP server
	PORT := ":8080"
	println("Server is running on port", PORT)
	http.ListenAndServe(PORT, nil)
}
