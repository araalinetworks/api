/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

// configCmd represents the config command
var configCmd = &cobra.Command{
	Use:   "config",
	Short: "Configure GoShelly for use in your system.",
	Long: ``,
	Run: func(cmd *cobra.Command, args []string) {
		
		os.MkdirAll("./logs/server-connections/", os.ModePerm)
		os.MkdirAll("./logs/client-connections/", os.ModePerm)
		os.MkdirAll("./logs/serverlogs/", os.ModePerm)
		os.MkdirAll("./logs/clientlogs/", os.ModePerm)
		fmt.Println("GoShelly configured. You are good to go :)")
	},
}

func init() {
	rootCmd.AddCommand(configCmd)
}
