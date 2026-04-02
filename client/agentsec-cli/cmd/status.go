package cmd

import (
	"agentsec-cli/internal/api"
	"agentsec-cli/internal/output"

	"github.com/spf13/cobra"
)

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show current status",
	Run: func(cmd *cobra.Command, args []string) {
		baseURL, _ := cmd.Flags().GetString("local-api")
		client, err := api.NewLocalClient(baseURL)
		if err != nil {
			output.PrintWarning("local api token unavailable, set AGENTSEC_PID or AGENTSEC_LOCAL_TOKEN")
			return
		}
		var payload map[string]any
		if err := client.GetPublic("/agentsec/health", &payload); err != nil {
			output.PrintError(err.Error())
			return
		}
		output.PrintMap(payload)
	},
}

func init() {
	statusCmd.Flags().String("local-api", "http://127.0.0.1:13133", "Local AgentSec API base URL")
	rootCmd.AddCommand(statusCmd)
}
