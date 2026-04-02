package registration

import (
	"agentsec-cli/internal/api"
	"net"
	"os"
	"runtime"

	"github.com/google/uuid"
)

type Fingerprint = api.Fingerprint

func CollectFingerprint(sdkVersion string) (Fingerprint, error) {
	hostname, err := os.Hostname()
	if err != nil {
		return Fingerprint{}, err
	}
	return Fingerprint{
		Hostname:   hostname,
		MachineID:  uuid.NewSHA1(uuid.NameSpaceDNS, []byte(hostname)).String(),
		OS:         runtime.GOOS,
		Arch:       runtime.GOARCH,
		IP:         localIP(),
		SDKVersion: sdkVersion,
	}, nil
}

func localIP() string {
	addrs, err := net.InterfaceAddrs()
	if err != nil {
		return "127.0.0.1"
	}
	for _, addr := range addrs {
		ipNet, ok := addr.(*net.IPNet)
		if !ok || ipNet.IP.IsLoopback() {
			continue
		}
		if ipNet.IP.To4() != nil {
			return ipNet.IP.String()
		}
	}
	return "127.0.0.1"
}
