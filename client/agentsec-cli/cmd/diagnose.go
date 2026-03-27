package cmd

import "github.com/spf13/cobra"

var diagnoseCmd = &cobra.Command{
	Use:   "diagnose",
	Short: "Diagnose local environment",
	Run: func(cmd *cobra.Command, args []string) {
		// diagnose logic
	},
}

func init() {
	rootCmd.AddCommand(diagnoseCmd)
}
