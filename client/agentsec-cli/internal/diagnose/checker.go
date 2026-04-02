package diagnose

import (
	"agentsec-cli/internal/auth"
	"crypto/tls"
	"fmt"
	"net"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

type CheckResult struct {
	Name    string
	OK      bool
	Message string
}

func RunAllChecks() []CheckResult {
	platformURL := strings.TrimSpace(os.Getenv("AGENTSEC_PLATFORM_URL"))
	collectorURL := strings.TrimSpace(os.Getenv("AGENTSEC_COLLECTOR_URL"))
	results := []CheckResult{
		{
			Name:    "platform_url",
			OK:      platformURL != "",
			Message: "platform endpoint can be configured with AGENTSEC_PLATFORM_URL",
		},
		{
			Name:    "collector_url",
			OK:      collectorURL != "",
			Message: "collector endpoint can be configured with AGENTSEC_COLLECTOR_URL",
		},
	}

	token, err := auth.ReadToken()
	if err != nil || token == "" {
		results = append(results, CheckResult{Name: "token", OK: false, Message: "cached token missing"})
	} else {
		info := auth.InspectToken(token)
		results = append(results, CheckResult{Name: "token_format", OK: info.Valid, Message: "JWT payload can be decoded"})
		results = append(results, CheckResult{Name: "token_expiry", OK: info.Status != "expired", Message: tokenExpiryMessage(info)})
	}

	if collectorURL != "" {
		results = append(results, checkCollectorReachable(collectorURL))
		results = append(results, checkTLSHandshake(collectorURL))
		results = append(results, checkCollectorAuth(collectorURL))
	}

	return results
}

func checkCollectorReachable(raw string) CheckResult {
	hostPort := collectorHostPort(raw)
	conn, err := net.DialTimeout("tcp", hostPort, 3*time.Second)
	if err == nil {
		_ = conn.Close()
		return CheckResult{Name: "collector_reachable", OK: true, Message: "collector tcp reachable"}
	}
	return CheckResult{Name: "collector_reachable", OK: false, Message: "collector tcp unreachable"}
}

func checkTLSHandshake(raw string) CheckResult {
	u, err := normalizeURL(raw)
	if err != nil {
		return CheckResult{Name: "tls_handshake", OK: false, Message: "collector URL is invalid"}
	}
	if u.Scheme != "https" {
		return CheckResult{Name: "tls_handshake", OK: true, Message: "collector does not use TLS"}
	}
	conn, err := tls.DialWithDialer(&net.Dialer{Timeout: 5 * time.Second}, "tcp", hostWithDefaultPort(u), &tls.Config{
		ServerName: strings.Split(u.Host, ":")[0],
		MinVersion: tls.VersionTLS12,
	})
	if err != nil {
		return CheckResult{Name: "tls_handshake", OK: false, Message: "TLS handshake failed"}
	}
	_ = conn.Close()
	return CheckResult{Name: "tls_handshake", OK: true, Message: "TLS handshake succeeded"}
}

func checkCollectorAuth(raw string) CheckResult {
	u, err := normalizeURL(raw)
	if err != nil {
		return CheckResult{Name: "collector_auth", OK: false, Message: "collector URL is invalid"}
	}
	if u.Scheme != "http" && u.Scheme != "https" {
		return CheckResult{Name: "collector_auth", OK: true, Message: "collector auth probe skipped for gRPC endpoint"}
	}
	endpoint := strings.TrimRight(u.String(), "/") + "/v1/traces"
	req, err := http.NewRequest(http.MethodPost, endpoint, strings.NewReader("{}"))
	if err != nil {
		return CheckResult{Name: "collector_auth", OK: false, Message: "collector auth probe build failed"}
	}
	req.Header.Set("Authorization", "Bearer invalid-token")
	req.Header.Set("Content-Type", "application/json")
	resp, err := (&http.Client{Timeout: 5 * time.Second}).Do(req)
	if err != nil {
		return CheckResult{Name: "collector_auth", OK: false, Message: "collector auth probe failed"}
	}
	defer resp.Body.Close()
	if resp.StatusCode == http.StatusUnauthorized || resp.StatusCode == http.StatusForbidden {
		return CheckResult{Name: "collector_auth", OK: true, Message: "collector rejects invalid token as expected"}
	}
	if resp.StatusCode >= 500 {
		return CheckResult{Name: "collector_auth", OK: false, Message: fmt.Sprintf("collector auth probe returned %d", resp.StatusCode)}
	}
	return CheckResult{Name: "collector_auth", OK: true, Message: fmt.Sprintf("collector responded with %d", resp.StatusCode)}
}

func normalizeURL(raw string) (*url.URL, error) {
	if strings.HasPrefix(raw, "http://") || strings.HasPrefix(raw, "https://") {
		return url.Parse(raw)
	}
	return url.Parse("http://" + raw)
}

func collectorHostPort(raw string) string {
	u, err := normalizeURL(raw)
	if err != nil {
		return raw
	}
	return hostWithDefaultPort(u)
}

func hostWithDefaultPort(u *url.URL) string {
	if strings.Contains(u.Host, ":") {
		return u.Host
	}
	if u.Scheme == "https" {
		return u.Host + ":443"
	}
	return u.Host + ":80"
}

func tokenExpiryMessage(info auth.TokenInfo) string {
	if info.Status == "expired" && info.ExpiresAt != nil {
		return "token expired at " + info.ExpiresAt.Format(time.RFC3339)
	}
	if info.ExpiresAt != nil {
		return "token valid until " + info.ExpiresAt.Format(time.RFC3339)
	}
	if info.Valid {
		return "token has no exp claim"
	}
	return "token payload invalid"
}
