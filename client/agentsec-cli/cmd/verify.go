package cmd

import "github.com/spf13/cobra"

var verifyCmd = &cobra.Command{
	Use:   "verify",
	Short: "Verify SDK connection",
	Run: func(cmd *cobra.Command, args []string) {
		// verify logic
	},
}

func init() {
	rootCmd.AddCommand(verifyCmd)
}
