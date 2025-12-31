package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sync"
)

// RenameTask represents a single rename operation
type RenameTask struct {
	SourcePath string `json:"src"`
	DestPath   string `json:"dst"`
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Error: No task data provided")
		os.Exit(1)
	}

	// Python passes tasks as a JSON string argument
	jsonData := os.Args[1]
	var tasks []RenameTask

	err := json.Unmarshal([]byte(jsonData), &tasks)
	if err != nil {
		fmt.Printf("Error parsing JSON: %v\n", err)
		os.Exit(1)
	}

	var wg sync.WaitGroup
	fmt.Printf("🚀 [Go Engine] Starting bulk processing of %d items...\n", len(tasks))

	// Channel to report results safely
	results := make(chan string, len(tasks))

	for _, task := range tasks {
		wg.Add(1)
		// Go routines for concurrency (Speed!)
		go func(t RenameTask) {
			defer wg.Done()
			processRename(t, results)
		}(task)
	}

	wg.Wait()
	close(results)

	// Print summary
	for res := range results {
		fmt.Println(res)
	}
}

func processRename(t RenameTask, results chan<- string) {
	// check if source exists
	info, err := os.Stat(t.SourcePath)
	if os.IsNotExist(err) {
		results <- fmt.Sprintf("❌ Skipped (Not Found): %s", filepath.Base(t.SourcePath))
		return
	}

	// Rename operation
	err = os.Rename(t.SourcePath, t.DestPath)
	if err != nil {
		results <- fmt.Sprintf("❌ Error Renaming %s: %v", filepath.Base(t.SourcePath), err)
		return
	}

	itemType := "File"
	if info.IsDir() {
		itemType = "Folder"
	}
	results <- fmt.Sprintf("✅ [Go] Renamed %s: '%s' -> '%s'", itemType, filepath.Base(t.SourcePath), filepath.Base(t.DestPath))
}