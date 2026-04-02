package api

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

type Client struct {
	BaseURL    string
	HTTPClient *http.Client
}

type Fingerprint struct {
	Hostname   string `json:"hostname"`
	MachineID  string `json:"machine_id"`
	OS         string `json:"os"`
	Arch       string `json:"arch"`
	IP         string `json:"ip"`
	SDKVersion string `json:"sdk_version"`
}

type AutoRegisterResponse struct {
	Status     string `json:"status"`
	AgentID    string `json:"agent_id"`
	TenantID   string `json:"tenant_id"`
	AgentToken string `json:"agent_token"`
	Token      string `json:"token"`
	ExpiresAt  string `json:"expires_at"`
}

type VerifySpanResponse struct {
	Received   bool   `json:"received"`
	ReceivedAt string `json:"received_at"`
}

func NewClient(baseURL string) *Client {
	return &Client{
		BaseURL: strings.TrimRight(baseURL, "/"),
		HTTPClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (c *Client) AutoRegister(ctx context.Context, fingerprint Fingerprint) (string, error) {
	body, err := json.Marshal(map[string]any{"fingerprint": fingerprint})
	if err != nil {
		return "", err
	}
	body, err = json.Marshal(map[string]any{
		"hostname":      fingerprint.Hostname,
		"os":            fingerprint.OS,
		"arch":          fingerprint.Arch,
		"machine_id":    fingerprint.MachineID,
		"ips":           []string{fingerprint.IP},
		"agent_version": fingerprint.SDKVersion,
		"sdk_version":   fingerprint.SDKVersion,
	})
	if err != nil {
		return "", err
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.BaseURL+"/api/v1/agents/auto-register", bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		return "", fmt.Errorf("auto-register failed with status %d", resp.StatusCode)
	}
	var payload AutoRegisterResponse
	if err := json.NewDecoder(resp.Body).Decode(&payload); err != nil {
		return "", err
	}
	if payload.AgentToken != "" {
		return payload.AgentToken, nil
	}
	return payload.Token, nil
}

func (c *Client) CheckSpanReceived(ctx context.Context, token, spanID string) (VerifySpanResponse, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.BaseURL+"/internal/verify-span?span_id="+spanID, nil)
	if err != nil {
		return VerifySpanResponse{}, err
	}
	if token != "" {
		req.Header.Set("Authorization", "Bearer "+token)
	}
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return VerifySpanResponse{}, err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		return VerifySpanResponse{}, fmt.Errorf("verify-span failed with status %d", resp.StatusCode)
	}
	var payload VerifySpanResponse
	if err := json.NewDecoder(resp.Body).Decode(&payload); err != nil {
		return VerifySpanResponse{}, err
	}
	return payload, nil
}
