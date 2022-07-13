package cmd

import (
	"fmt"
	b "goshelly-client/basic"
	"os"
	"strings"

	"github.com/spf13/cobra"
)

var deleteURL = "/delete/"

// deleteCmd represents the delete command
var deleteCmd = &cobra.Command{
	Use:   "delete",
	Short: "Delete account.",
	Long:  `Delete's all existence of the user's account and data from the GoShelly Server.`,
	Run: func(cmd *cobra.Command, args []string) {
		if !b.LoginStatus(URLHEAD+statusURL) {
			fmt.Println("Signup and/or login into your GoShelly account to continue.")
			return
		}
		var temp string
		var confirm bool
		fmt.Printf("NOTE: Running delete will delete your account permanently.")
		fmt.Println("All data associated with your account will also be removed permanently.")
		fmt.Printf("Are you sure you would like to delete your account? (Y/N) --> ")
		fmt.Scanf("%s", &temp)
		temp = strings.ToLower(temp)
		switch temp {
		case "y":
			confirm = true
		case "n":
			confirm = false
		default:
			return
		}

		b.DeleteUser(confirm, URLHEAD+deleteURL)
		os.Remove("./config/token-config.json")
	},
}

func init() {
	rootCmd.AddCommand(deleteCmd)
}
