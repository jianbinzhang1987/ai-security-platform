package cmd

import (
	"agentsec-cli/internal/diagnose"
	"agentsec-cli/internal/output"

	"github.com/spf13/cobra"
)

var diagnoseCmd = &cobra.Command{
	Use:   "diagnose",
	Short: "Diagnose local environment",
	Run: func(cmd *cobra.Command, args []string) {
		allOK := true
		for _, check := range diagnose.RunAllChecks() {
			if check.OK {
				output.PrintSuccess(check.Name + ": " + check.Message)
				continue
			}
			allOK = false
			output.PrintWarning(check.Name + ": " + check.Message)
		}
		if !allOK {
			output.PrintError("diagnostics found issues")
		}
	},
}

func init() {
	rootCmd.AddCommand(diagnoseCmd)
}
