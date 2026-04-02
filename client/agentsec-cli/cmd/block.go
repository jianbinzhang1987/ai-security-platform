package cmd

import (
	"agentsec-cli/internal/api"
	"agentsec-cli/internal/output"
	"fmt"

	"github.com/spf13/cobra"
)

var blockCmd = &cobra.Command{
	Use:   "block",
	Short: "Inspect local block status",
	Run: func(cmd *cobra.Command, args []string) {
		baseURL, _ := cmd.Flags().GetString("local-api")
		client, err := api.NewLocalClient(baseURL)
		if err != nil {
			output.PrintError(err.Error())
			return
		}
		var payload map[string]any
		if err := client.Get("/agentsec/block/status", &payload); err != nil {
			output.PrintError(err.Error())
			return
		}
		for _, key := range []string{"block_count", "ws_connected", "last_ws_message_at"} {
			output.PrintKV(key, payload[key])
		}
		if blocks, ok := payload["active_blocks"].([]any); ok {
			for index, raw := range blocks {
				item, ok := raw.(map[string]any)
				if !ok {
					continue
				}
				output.PrintInfo(fmt.Sprintf("active_block[%d]", index))
				output.PrintMap(item)
			}
		}
	},
}

func init() {
	blockCmd.Flags().String("local-api", "http://127.0.0.1:13133", "Local AgentSec API base URL")
	rootCmd.AddCommand(blockCmd)
}
