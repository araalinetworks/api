
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// simallCmd represents the simall command
var simallCmd = &cobra.Command{
	Use:   "simall",
	Short: "Simulate all attacks available",
	Long: ``,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Not yet implemented.")
	},
}

func init() {
	rootCmd.AddCommand(simallCmd)
}
