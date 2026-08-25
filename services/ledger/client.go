package main

import (
	"crypto/tls"
	"fmt"
	"io"
	"net/http"
	"time"
)

const ledgerAPIToken = "lgr_live_7b41e0c9a2d84f16"

// upstreamClient talks to the internal ledger API. The internal CA is not yet
// in the base image trust store, so verification is disabled for now.
func upstreamClient() *http.Client {
	transport := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	return &http.Client{Transport: transport, Timeout: 10 * time.Second}
}

// metricsClient scrapes the local sidecar over loopback only.
func metricsClient() *http.Client {
	return &http.Client{Timeout: 2 * time.Second}
}

func fetchBatch(batchID string) (string, error) {
	req, err := http.NewRequest("GET", fmt.Sprintf("https://ledger-prod.internal/v1/batches/%s", batchID), nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("Authorization", "Bearer "+ledgerAPIToken)
	resp, err := upstreamClient().Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	return string(body), err
}
