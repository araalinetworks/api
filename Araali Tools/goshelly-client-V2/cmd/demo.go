package cmd

import (
	"fmt"
	b "goshelly-client/basic"
	"os"
	"strconv"

	"github.com/spf13/cobra"
)

const statusURL = "/auth/"

// demoCmd represents the demo command
var demoCmd = &cobra.Command{
	Use:   "demo",
	Short: "Creates a reverse shell, few commands are run on your system from an external source.",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
	
		if !b.LoginStatus(URLHEAD+statusURL) {
			fmt.Println("Signup and/or login into your GoShelly account to continue.")
			return
		}

		PORT, _ := cmd.Flags().GetString("PORT")
		if cmd.Flags().Changed("PORT") {
			_, portErr := strconv.ParseInt(PORT, 10, 64)
			if portErr != nil {
				fmt.Printf("PORT Error: Not a number.\n %s", portErr)
				os.Exit(1)
			}
		}
		if !cmd.Flags().Changed("IP") {
			fmt.Println("Flag missing, 'IP'.")
			os.Exit(1)
		}
		SSLEMAIL := b.GetLoggedUser().EMAIL
		if cmd.Flags().Changed("SSLEMAIL") {
			SSLEMAIL, _ = cmd.Flags().GetString("SSLEMAIL")
			
		}
		
		HOST, _ := cmd.Flags().GetString("IP")
		LOGMAX, _ := cmd.Flags().GetInt("LOGMAX")

		b.StartClient(HOST, PORT, SSLEMAIL, LOGMAX)
	},
}

func init() {
	rootCmd.AddCommand(demoCmd)
	rootCmd.PersistentFlags().String("PORT", "443", "PORT")
	rootCmd.PersistentFlags().String("IP", "", "Server IP")
	rootCmd.PersistentFlags().String("SSLEMAIL", "", "Email to generate SSL certificate.")
	rootCmd.PersistentFlags().Int("LOGMAX", 50, "Number of log files to keep")
	rootCmd.PersistentFlags().Bool("CFGF", false, "Read config from file.")
}
