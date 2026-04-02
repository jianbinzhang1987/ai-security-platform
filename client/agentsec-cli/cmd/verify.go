package cmd

import (
	"agentsec-cli/internal/api"
	"agentsec-cli/internal/auth"
	"agentsec-cli/internal/collector"
	"agentsec-cli/internal/output"
	"time"

	"github.com/spf13/cobra"
)

var verifyCmd = &cobra.Command{
	Use:   "verify",
	Short: "Verify SDK connection",
	Run: func(cmd *cobra.Command, args []string) {
		collectorURL, _ := cmd.Flags().GetString("collector")
		token, _ := cmd.Flags().GetString("token")
		platformURL, _ := cmd.Flags().GetString("platform")
		if token == "" {
			if cached, err := auth.ReadToken(); err == nil {
				token = cached
			}
		}
		testSpanID, err := collector.SendTestSpan(cmd.Context(), collectorURL, token)
		if err != nil {
			output.PrintError(err.Error())
			return
		}
		if platformURL == "" || token == "" {
			output.PrintSuccess("collector verification succeeded")
			output.PrintInfo("span_id: " + testSpanID)
			return
		}
		client := api.NewClient(platformURL)
		for i := 0; i < 10; i++ {
			result, err := client.CheckSpanReceived(cmd.Context(), token, testSpanID)
			if err == nil && result.Received {
				output.PrintSuccess("platform verification succeeded")
				output.PrintKV("span_id", testSpanID)
				output.PrintKV("received_at", result.ReceivedAt)
				return
			}
			time.Sleep(time.Second)
		}
		output.PrintWarning("collector export succeeded but platform verification timed out")
		output.PrintInfo("span_id: " + testSpanID)
	},
}

func init() {
	verifyCmd.Flags().StringP("token", "t", "", "Agent Token")
	verifyCmd.Flags().StringP("collector", "c", "localhost:4317", "Collector OTLP gRPC endpoint")
	verifyCmd.Flags().String("platform", "", "Platform base URL for verify-span polling")
	rootCmd.AddCommand(verifyCmd)
}
