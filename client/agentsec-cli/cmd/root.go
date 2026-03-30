package cmd

import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{
	Use:   "agentsec-cli",
	Short: "AI Agent Security Platform CLI",
}

func Execute() {
	rootCmd.Execute()
}
