package cmd

import "github.com/spf13/cobra"

var tracesCmd = &cobra.Command{
	Use:   "traces",
	Short: "List or get traces",
}

func init() {
	rootCmd.AddCommand(tracesCmd)
}
