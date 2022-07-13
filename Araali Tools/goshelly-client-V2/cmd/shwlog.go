package cmd

import (
	"encoding/json"
	"fmt"
	b "goshelly-client/basic"
	t "goshelly-client/template"
	"io/ioutil"
	"net/http"
	"net/url"
	"strconv"
	"github.com/spf13/cobra"
)

const logURL = "/link/"
const discprompt = 
`NOTE: Each requested log is made available for a short period of time at the URL returned.
Changing parts of this link will NOT lead to other logs. This link is not transferrable, 
only the requesting computer will be able to access the contents of the link generated.
	`

// shwlogCmd represents the shwlog command
var shwlogCmd = &cobra.Command{
	Use:   "shwlog",
	Short: "See logs from your GoShelly runs.",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		if !b.LoginStatus(URLHEAD+statusURL) {
			fmt.Println("Signup and/or login into your GoShelly account to continue.")
			return
		}

		if !cmd.Flags().Changed("ID") {
			fmt.Println("Please specify a log ID to fetch.")
			return

		}
		inputIDS, _ := cmd.Flags().GetString("ID")
		genLinks(inputIDS)
	},
}

func genLinks(ids string) {
	fmt.Println("Fetching log for log ID: ", ids)
	var obj t.Msg
	tempUser := b.GetLoggedUser()
	i, _ := strconv.Atoi(ids)
	user := t.UserLinks{
		EMAIL: tempUser.EMAIL,
		TOKEN: tempUser.TOKEN,
		LOGID: i,
	}
	resp := b.SendPOST(URLHEAD+logURL, user)
	body, err := ioutil.ReadAll(resp.Body)
	
	if err != nil {
		fmt.Println(resp.StatusCode, "Could not read response.")
		return
	}

	json.Unmarshal(body, &obj)
	if resp.StatusCode != http.StatusOK {
		fmt.Println(obj.MESSAGE)
		return
	}
	u, err := url.Parse(obj.MESSAGE)
	if err != nil {
		fmt.Println("Could not parse log link.")
	}
	
	fmt.Printf("\nYou can find the requested log here: %+v\n\n", u)
	fmt.Println(discprompt)
	
}

func init() {
	rootCmd.AddCommand(shwlogCmd)
	rootCmd.PersistentFlags().String("ID", "", "Host the log data for a Goshelly run ID. E[1,5]")
}
