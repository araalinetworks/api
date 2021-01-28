package main

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"syscall"
)

// FileExists - check if file exists
func FileExists(filename string) bool {
	_, err := os.Stat(filename)
	if os.IsNotExist(err) {
		return false
	}
	return true
}

// CommandDebug - logs every command that is executed
var CommandDebug = false

// RunControlOut takes a command and runs it, control is for whether to exit, allows output to go to stdout
func RunControlOut(cmdArgs []string, user string, exitOnFailure bool, out *bytes.Buffer) error {
	if CommandDebug {
		fmt.Println(cmdArgs, user, exitOnFailure)
	}
	cmd := exec.Command(cmdArgs[0], cmdArgs[1:]...)
	cmd.Env = os.Environ()
	if len(user) != 0 {
		cmd.SysProcAttr = &syscall.SysProcAttr{}
		uids, _ := RunControl([]string{"id", "-u", user}, "", true)
		uid, _ := strconv.Atoi(strings.TrimSpace(uids))
		gids, _ := RunControl([]string{"id", "-g", user}, "", true)
		gid, _ := strconv.Atoi(strings.TrimSpace(gids))
		cmd.SysProcAttr.Credential = &syscall.Credential{Uid: uint32(uid), Gid: uint32(gid)}
	}

	if out != nil {
		cmd.Stdout = out
		//cmd.Stderr = out // comment to not capture stderr
	} else {
		cmd.Stdin = os.Stdin
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
	}

	if err := cmd.Run(); err != nil {
		if exitOnFailure {
			fmt.Fprintln(os.Stderr, strings.Join(cmdArgs, " ")+": "+fmt.Sprint(err)+": "+out.String())
			os.Exit(1)
		} else {
			return err
		}
	}
	return nil
}

// RunControl takes a command and runs it, control is for whether to exit
func RunControl(cmdArgs []string, user string, exitOnFailure bool) (string, error) {
	var out bytes.Buffer
	err := RunControlOut(cmdArgs, user, exitOnFailure, &out)
	if err == nil {
		return out.String(), nil
	}
	return "", err
}

// RunStrControl takes a command string and runs it, control is for whether to exit
func RunStrControl(cmdstr, user string, exitOnFailure bool) (string, error) {
	return RunControl([]string{"sh", "-c", cmdstr}, user, exitOnFailure)
}

// RunAs - Run cmdstr as user
func RunAs(cmdstr, user string) string {
	ret, _ := RunStrControl(cmdstr, user, true)
	return ret
}

// RunCmd - Run cmdstr and collect/return output
func RunCmd(cmdstr string) string {
	return RunAs(cmdstr, "")
}

// GetZones - return zones and apps, use tenant="" by default
func GetZones(full bool, tenant string) string {
	tenantStr := func() string {
		if len(tenant) == 0 {
			return ""
		}
		return "-tenant=" + tenant
	}()
	fullStr := func() string {
		if full {
			return "-full"
		}
		return ""
	}()

	return RunCmd(fmt.Sprintf("/opt/araali/bin/araalictl api -fetch-zone-apps %s %s", fullStr, tenantStr))
	// XXX convert to yaml and return
}
