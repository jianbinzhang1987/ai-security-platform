package auth

import (
	"encoding/base64"
	"fmt"
	"testing"
	"time"
)

func buildToken(payload string) string {
	header := base64.RawURLEncoding.EncodeToString([]byte(`{"alg":"none"}`))
	body := base64.RawURLEncoding.EncodeToString([]byte(payload))
	return fmt.Sprintf("%s.%s.signature", header, body)
}

func TestInspectTokenExpired(t *testing.T) {
	token := buildToken(fmt.Sprintf(`{"exp":%d,"tenant_id":"t1"}`, time.Now().Add(-time.Hour).Unix()))
	info := InspectToken(token)
	if info.Status != "expired" {
		t.Fatalf("expected expired status, got %s", info.Status)
	}
	if info.Claims["tenant_id"] != "t1" {
		t.Fatalf("expected tenant_id t1, got %#v", info.Claims["tenant_id"])
	}
}
