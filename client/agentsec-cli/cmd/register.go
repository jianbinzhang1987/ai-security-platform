package cmd

import (
	"agentsec-cli/internal/api"
	"agentsec-cli/internal/auth"
	"agentsec-cli/internal/output"
	"agentsec-cli/internal/registration"

	"github.com/spf13/cobra"
)

var registerCmd = &cobra.Command{
	Use:   "register",
	Short: "Auto-register the current machine and cache the agent token",
	Run: func(cmd *cobra.Command, args []string) {
		platformURL, _ := cmd.Flags().GetString("platform")
		sdkVersion, _ := cmd.Flags().GetString("sdk-version")
		fingerprint, err := registration.CollectFingerprint(sdkVersion)
		if err != nil {
			output.PrintError(err.Error())
			return
		}
		client := api.NewClient(platformURL)
		token, err := client.AutoRegister(cmd.Context(), api.Fingerprint{
			Hostname:   fingerprint.Hostname,
			MachineID:  fingerprint.MachineID,
			OS:         fingerprint.OS,
			Arch:       fingerprint.Arch,
			IP:         fingerprint.IP,
			SDKVersion: fingerprint.SDKVersion,
		})
		if err != nil {
			output.PrintError(err.Error())
			return
		}
		if err := auth.WriteToken(token); err != nil {
			output.PrintError(err.Error())
			return
		}
		output.PrintSuccess("agent token cached successfully")
		output.PrintKV("platform", platformURL)
		output.PrintKV("hostname", fingerprint.Hostname)
		output.PrintKV("machine_id", fingerprint.MachineID)
	},
}

func init() {
	registerCmd.Flags().String("platform", "http://localhost:8080", "Platform base URL")
	registerCmd.Flags().String("sdk-version", "0.1.0", "SDK version included in the fingerprint")
	rootCmd.AddCommand(registerCmd)
}
