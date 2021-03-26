package main

import (
	"../../araalictl"
)

func testLinks() {
	app := araalictl.App{ZoneName: "staging", AppName: "bend"}
	app.Refresh()
	app.Links[0].Snooze()
	app.Links[0].Accept()
	app.Links[2].Deny()
	// The above marks the local cache for those actions.
	// Once we are done with the link manipulations, we
	// commit them as below to take effect.
	// output := app.Commit()
	// fmt.Println(output)
}
