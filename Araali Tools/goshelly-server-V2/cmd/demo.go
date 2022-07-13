
package cmd

import (
	s "goshelly-server/basic"
	"fmt"
	"os"
	"strconv"

	"github.com/spf13/cobra"
	api "goshelly-server/goshelly-server-api"
)



// demoCmd represents the demo command
var demoCmd = &cobra.Command{
	Use:   "demo",
	Short: "Run a set of cli commands.",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) { 
		s.CheckIfConfig()
		fmt.Println("Running GoShelly Server - Demo.")
		PORT, _ := cmd.Flags().GetString("PORT")
		_, portErr := strconv.ParseInt(PORT,10, 64)
		if portErr != nil {
			fmt.Printf("PORT Error: Not a number.\n %s", portErr)
			os.Exit(1)
		}
		SSL_EMAIL, _  := cmd.Flags().GetString("SSLEMAIL")
		NOT_EMAIL, _  := cmd.Flags().GetString("NOTEMAIL")
		HOOK_SLACK, _  := cmd.Flags().GetString("SLACKHOOK")
		EMAIL_EN, _ := cmd.Flags().GetBool("EMAILEN")
		SLACK_EN, _ := cmd.Flags().GetBool("SLACKEN")
		CMDS_TO_RUN := []string{"ls", "uname -a", "whoami", "pwd", "env"}
		SERV_LOG_MAX, _ := cmd.Flags().GetInt("SERVLOGMAX")
		CLI_LOG_MAX, _ := cmd.Flags().GetInt("CLILOGMAX")
		if SERV_LOG_MAX < 0 || CLI_LOG_MAX < 0{
			fmt.Println("*LOGMAX: Cannot be a negative number")
			os.Exit(1)
		}


		fmt.Println("Starting API-Server...")
		APIHOSTPORT := "9000"
		go api.BeginAPI(APIHOSTPORT)
		s.StartServer(PORT, SSL_EMAIL, NOT_EMAIL, HOOK_SLACK, EMAIL_EN, SLACK_EN, CMDS_TO_RUN, "DEMO", SERV_LOG_MAX, CLI_LOG_MAX) 
	},
}

func init() {
	rootCmd.AddCommand(demoCmd)
	demoCmd.PersistentFlags().String("PORT", "443", "PORT to listen for incoming connections.")
	demoCmd.PersistentFlags().String("SSLEMAIL", "goshellydemo@araalinetworks.com", "Email address to generate SSL certificate.")
	demoCmd.PersistentFlags().String("NOTEMAIL", "all@araalinetworks.com", "Email to be notified after a client is connected.")
	demoCmd.PersistentFlags().String("SLACKHOOK", "", "SLACK HOOK")
	demoCmd.PersistentFlags().Bool("SLACKEN", false, "Enable/Disable slack notifications")
	demoCmd.PersistentFlags().Bool("EMAILEN", false, "Enable/Disable email notifications")
	demoCmd.PersistentFlags().Int("SERVLOGMAX", 50, "Max number of log files to save for server.")
	demoCmd.PersistentFlags().Int("CLILOGMAX", 5, "Max number of log files to save each client.")
}
