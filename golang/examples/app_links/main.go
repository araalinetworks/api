package main

import (
	"fmt"

	"../../araalictl"
)

func main() {
	app := araalictl.App{ZoneName: "prod", AppName: "bendvm"}
	app.Refresh()
	app.Links[0].Snooze()
	app.Links[0].Accept()
	app.Links[2].Deny()
	output := app.Commit()
	fmt.Println(output)
}
