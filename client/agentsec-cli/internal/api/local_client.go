package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
)

type LocalClient struct {
	BaseURL    string
	Token      string
	HTTPClient *http.Client
}

func NewLocalClient(baseURL string) (*LocalClient, error) {
	token, err := readLocalToken()
	if err != nil {
		return nil, err
	}
	return &LocalClient{
		BaseURL: strings.TrimRight(baseURL, "/"),
		Token:   token,
		HTTPClient: &http.Client{
			Timeout: 5 * time.Second,
		},
	}, nil
}

func readLocalToken() (string, error) {
	if token := strings.TrimSpace(os.Getenv("AGENTSEC_LOCAL_TOKEN")); token != "" {
		return token, nil
	}
	pid := os.Getenv("AGENTSEC_PID")
	if pid == "" {
		matches, err := filepath.Glob(filepath.Join(os.TempDir(), "agentsec-*.token"))
		if err != nil || len(matches) == 0 {
			return "", fmt.Errorf("local api token unavailable, set AGENTSEC_LOCAL_TOKEN or AGENTSEC_PID")
		}
		sort.Slice(matches, func(i, j int) bool {
			left, lerr := os.Stat(matches[i])
			right, rerr := os.Stat(matches[j])
			if lerr != nil || rerr != nil {
				return matches[i] > matches[j]
			}
			return left.ModTime().After(right.ModTime())
		})
		pidPath := matches[0]
		data, err := os.ReadFile(pidPath)
		if err != nil {
			return "", err
		}
		return strings.TrimSpace(string(data)), nil
	}
	data, err := os.ReadFile(filepath.Join(os.TempDir(), "agentsec-"+pid+".token"))
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(data)), nil
}

func (c *LocalClient) Get(path string, target any) error {
	req, err := http.NewRequest(http.MethodGet, c.BaseURL+path, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.Token)
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		return fmt.Errorf("local api returned %d", resp.StatusCode)
	}
	return json.NewDecoder(resp.Body).Decode(target)
}

func (c *LocalClient) GetPublic(path string, target any) error {
	resp, err := c.HTTPClient.Get(c.BaseURL + path)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		return fmt.Errorf("local api returned %d", resp.StatusCode)
	}
	return json.NewDecoder(resp.Body).Decode(target)
}
