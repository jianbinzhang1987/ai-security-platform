package cmd

import "github.com/spf13/cobra"

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "Show current status",
	Run: func(cmd *cobra.Command, args []string) {
		// status logic
	},
}

func init() {
	rootCmd.AddCommand(statusCmd)
}
