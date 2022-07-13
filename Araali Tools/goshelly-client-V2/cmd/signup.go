package cmd

import (
	"fmt"
	b "goshelly-client/basic"
	t "goshelly-client/template"
	"net/http"
	"time"
	"github.com/spf13/cobra"
)

const signupURL = "/signup/"
var newUser t.User

var signupCmd = &cobra.Command{
	Use:   "signup",
	Short: "Create an account with Araali GoShelly",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("NOTE: A valid email and a password is required to sign up. Passwords cannot be reset.")
		fmt.Println("In the event you cannot remember your password, you will need to delete your account and all data with it.")
		time.Sleep(time.Second * 1)
		newUser.NAME,newUser.EMAIL,newUser.PASSWORD = b.GetCredentials(1)
		resp := b.SendPOST(URLHEAD+signupURL,newUser)
		b.PrintResp(resp)
		if resp.StatusCode == http.StatusCreated {
		LoginRun(URLHEAD+loginURL, t.LoginUser{
			EMAIL: newUser.EMAIL,
			PASSWORD: newUser.PASSWORD,
		})
	}

	},
}



func init() {
	rootCmd.AddCommand(signupCmd)
}
