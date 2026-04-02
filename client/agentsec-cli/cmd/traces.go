package cmd

import (
	"agentsec-cli/internal/api"
	"agentsec-cli/internal/output"
	"fmt"
	"net/url"
	"strconv"

	"github.com/spf13/cobra"
)

var tracesCmd = &cobra.Command{
	Use:   "traces",
	Short: "List or get traces",
	Run: func(cmd *cobra.Command, args []string) {
		baseURL, _ := cmd.Flags().GetString("local-api")
		limit, _ := cmd.Flags().GetInt("limit")
		offset, _ := cmd.Flags().GetInt("offset")
		spanType, _ := cmd.Flags().GetString("type")
		riskLevel, _ := cmd.Flags().GetString("risk-level")
		securityOnly, _ := cmd.Flags().GetBool("security-only")
		client, err := api.NewLocalClient(baseURL)
		if err != nil {
			output.PrintError(err.Error())
			return
		}
		query := url.Values{}
		query.Set("limit", strconv.Itoa(limit))
		query.Set("offset", strconv.Itoa(offset))
		if spanType != "" {
			query.Set("type", spanType)
		}
		if riskLevel != "" {
			query.Set("risk_level", riskLevel)
		}
		if securityOnly {
			query.Set("has_security_event", "true")
		}
		var payload map[string]any
		if err := client.Get("/agentsec/traces?"+query.Encode(), &payload); err != nil {
			output.PrintError(err.Error())
			return
		}
		output.PrintKV("total", payload["total"])
		output.PrintKV("limit", payload["limit"])
		output.PrintKV("offset", payload["offset"])
		items, _ := payload["items"].([]any)
		for _, raw := range items {
			traceItem, ok := raw.(map[string]any)
			if !ok {
				continue
			}
			output.PrintInfo("---")
			for _, key := range []string{"trace_id", "risk_level", "span_count", "span_types", "security_events"} {
				output.PrintKV(key, traceItem[key])
			}
		}
	},
}

var traceGetCmd = &cobra.Command{
	Use:   "get [trace_id]",
	Short: "Get trace detail from local AgentSec API",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		baseURL, _ := cmd.Flags().GetString("local-api")
		client, err := api.NewLocalClient(baseURL)
		if err != nil {
			output.PrintError(err.Error())
			return
		}
		var traceDetail map[string]any
		if err := client.Get(fmt.Sprintf("/agentsec/traces/%s", args[0]), &traceDetail); err != nil {
			output.PrintError(err.Error())
			return
		}
		output.PrintMap(traceDetail)
	},
}

func init() {
	tracesCmd.Flags().String("local-api", "http://127.0.0.1:13133", "Local AgentSec API base URL")
	tracesCmd.Flags().Int("limit", 10, "Maximum number of traces to return")
	tracesCmd.Flags().Int("offset", 0, "Pagination offset")
	tracesCmd.Flags().String("type", "", "Filter by trace span type")
	tracesCmd.Flags().String("risk-level", "", "Filter by risk level")
	tracesCmd.Flags().Bool("security-only", false, "Only show traces with security events")
	traceGetCmd.Flags().String("local-api", "http://127.0.0.1:13133", "Local AgentSec API base URL")
	tracesCmd.AddCommand(traceGetCmd)
	rootCmd.AddCommand(tracesCmd)
}
