/*
Copyright © 2022 Soham Arora arorasoham9@gmail.com

*/
package cmd

import (
	"os"

	"github.com/spf13/cobra"
)



// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "goshelly-serv",
	Short: "",
	Long: `Araali GoShelly is an open source tool that helps security teams safely test their detect and response readiness (the fire drill for SIEM/SOAR/EDR/NDR/XDR investment) for backdoors. This is typical when supply chain vulnerabilities like remote code execution (RCE) are exploited and represents a doomsday scenario where an attacker has full remote control capabilities based on the backdoor.`,
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	// Here you will define your flags and configuration settings.
	// Cobra supports persistent flags, which, if defined here,
	// will be global for your application.

	// rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.cobrashelly.yaml)")

	// Cobra also supports local flags, which will only run
	// when this action is called directly.
	// rootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}


