/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>

*/
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
		fmt.Println("simall called")
		fmt.Println("Not yet implemented.")
	},
}

func init() {
	rootCmd.AddCommand(simallCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// simallCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// simallCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
