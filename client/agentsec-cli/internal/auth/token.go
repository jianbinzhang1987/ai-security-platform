package auth

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

type TokenInfo struct {
	Raw       string
	Claims    map[string]any
	Valid     bool
	Status    string
	ExpiresAt *time.Time
}

func cachePath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".agentsec", "agent.token"), nil
}

func ReadToken() (string, error) {
	if token := strings.TrimSpace(os.Getenv("AGENTSEC_TOKEN")); token != "" {
		return token, nil
	}
	path, err := cachePath()
	if err != nil {
		return "", err
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(data)), nil
}

func WriteToken(token string) error {
	path, err := cachePath()
	if err != nil {
		return err
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	return os.WriteFile(path, []byte(strings.TrimSpace(token)), 0o600)
}

func InspectToken(token string) TokenInfo {
	info := TokenInfo{
		Raw:    strings.TrimSpace(token),
		Claims: map[string]any{},
		Status: "missing",
	}
	if info.Raw == "" {
		return info
	}
	parts := strings.Split(info.Raw, ".")
	if len(parts) < 2 {
		info.Status = "invalid"
		return info
	}
	payload, err := base64.RawURLEncoding.DecodeString(parts[1])
	if err != nil {
		info.Status = "invalid"
		return info
	}
	if err := json.Unmarshal(payload, &info.Claims); err != nil {
		info.Status = "invalid"
		return info
	}
	info.Valid = true
	info.Status = "valid"
	if expValue, ok := info.Claims["exp"]; ok {
		switch value := expValue.(type) {
		case float64:
			ts := time.Unix(int64(value), 0).UTC()
			info.ExpiresAt = &ts
		case json.Number:
			if n, err := value.Int64(); err == nil {
				ts := time.Unix(n, 0).UTC()
				info.ExpiresAt = &ts
			}
		}
	}
	if info.ExpiresAt != nil && !info.ExpiresAt.After(time.Now().UTC()) {
		info.Status = "expired"
	}
	return info
}

func MustReadAndInspect() (TokenInfo, error) {
	token, err := ReadToken()
	if err != nil {
		return TokenInfo{}, err
	}
	info := InspectToken(token)
	if !info.Valid && info.Status != "expired" {
		return info, fmt.Errorf("invalid token format")
	}
	return info, nil
}
