package cmd

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	t "goshelly-client/template"
	"io/ioutil"
	"os"

	"github.com/spf13/cobra"
)

// chipCmd represents the chip command
var chipCmd = &cobra.Command{
	Use:   "chip",
	Short: "Change api server connection IP",
	Long:  ``,
	Run: func(cmd *cobra.Command, args []string) {
		temp := ""
		fmt.Printf("Enter connection address ->")
		fmt.Scanf("%s", &temp)
		os.MkdirAll("./config/", os.ModePerm)
		fo, err := os.Create("./config/api_conn_config.json")
		if err != nil {
			fmt.Println("Could not process connection IP.")
		}
		fo.Close()
		file, _ := json.MarshalIndent(t.ApiConnIP{
			IP: base64.StdEncoding.EncodeToString([]byte(temp)),
		}, "", " ")

		_ = ioutil.WriteFile("./config/api_conn_config.json", file, 0644)
		fmt.Println("Connection IP settings for this session will be stored as a json config in a non-encrypted format.")

	},
}

func init() {
	rootCmd.AddCommand(chipCmd)
}
