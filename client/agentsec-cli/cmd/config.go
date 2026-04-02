package cmd

import (
	"agentsec-cli/internal/api"
	"agentsec-cli/internal/output"
	"os"

	"github.com/spf13/cobra"
)

var configCmd = &cobra.Command{
	Use:   "config",
	Short: "Manage configuration",
	Run: func(cmd *cobra.Command, args []string) {
		output.PrintKV("AGENTSEC_PLATFORM_URL", os.Getenv("AGENTSEC_PLATFORM_URL"))
		output.PrintKV("AGENTSEC_COLLECTOR_URL", os.Getenv("AGENTSEC_COLLECTOR_URL"))
		output.PrintKV("AGENTSEC_TOKEN", os.Getenv("AGENTSEC_TOKEN") != "")
	},
}

var configStatusCmd = &cobra.Command{
	Use:   "status",
	Short: "Read config sync status from local AgentSec API",
	Run: func(cmd *cobra.Command, args []string) {
		baseURL, _ := cmd.Flags().GetString("local-api")
		client, err := api.NewLocalClient(baseURL)
		if err != nil {
			output.PrintError(err.Error())
			return
		}
		var payload map[string]any
		if err := client.Get("/agentsec/config/status", &payload); err != nil {
			output.PrintError(err.Error())
			return
		}
		output.PrintMap(payload)
	},
}

func init() {
	configStatusCmd.Flags().String("local-api", "http://127.0.0.1:13133", "Local AgentSec API base URL")
	configCmd.AddCommand(configStatusCmd)
	rootCmd.AddCommand(configCmd)
}
