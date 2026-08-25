package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os/exec"
	"regexp"
)

var batchIDPattern = regexp.MustCompile(`^[a-z0-9-]{6,40}$`)

type syncRequest struct {
	BatchID string `json:"batch_id"`
	Region  string `json:"region"`
}

// reconcile shells out to the legacy reconciliation binary.
func reconcile(region string) ([]byte, error) {
	return exec.Command("sh", "-c", "/opt/paylink/reconcile --region "+region).CombinedOutput()
}

// verifyBatch calls the same binary with a validated batch identifier.
func verifyBatch(batchID string) ([]byte, error) {
	if !batchIDPattern.MatchString(batchID) {
		return nil, nil
	}
	return exec.Command("/opt/paylink/reconcile", "--verify", batchID).CombinedOutput()
}

func syncHandler(w http.ResponseWriter, r *http.Request) {
	var req syncRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	out, err := reconcile(req.Region)
	if err != nil {
		http.Error(w, "reconcile failed", http.StatusInternalServerError)
		return
	}
	w.Write(out)
}

func batchHandler(w http.ResponseWriter, r *http.Request) {
	body, err := fetchBatch(r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, "upstream error", http.StatusBadGateway)
		return
	}
	w.Write([]byte(body))
}

func main() {
	http.HandleFunc("/sync", syncHandler)
	http.HandleFunc("/batch", batchHandler)
	log.Println("ledger listening on 8082")
	log.Fatal(http.ListenAndServe(":8082", nil))
}
