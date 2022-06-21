package main

import (
	// "bufio"
	"crypto/tls"
	"crypto/x509"
	"encoding/base64"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"strings"
	"time"

	"github.com/joho/godotenv"
)

func handleError(err error) {
	if err != nil {
		log.Fatal(err)
	}
}

// file upl /downl functions, if needed
func uploadFile(conn *tls.Conn, path string) {
	// open file to upload
	fi, err := os.Open(path)
	handleError(err)
	defer fi.Close()
	// upload
	_, err = io.Copy(conn, fi)
	handleError(err)
}

func downloadFile(conn *tls.Conn, path string) {
	// create new file to hold response
	fo, err := os.Create(path)
	handleError(err)
	defer fo.Close()

	handleError(err)
	defer conn.Close()

	_, err = io.Copy(fo, conn)
	handleError(err)
}

func execInput(input string) string {
	// Remove the newline character.
	input = strings.TrimSuffix(input, "\n")

	cmd, err := exec.Command("bash", "-c", input).Output()
	if err != nil {
		log.Fatal(err)
	}
	return string(cmd[:])
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
func setReadDeadLine(conn *tls.Conn) {
	err := conn.SetReadDeadline(time.Now().Add(10 * time.Second))
	if err != nil {
		log.Println("SetReadDeadline failed:", err)
	}
}

func setWriteDeadLine(conn *tls.Conn) {
	err := conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
	if err != nil {
		log.Println("SetWriteDeadline failed:", err)
	}
}

func dialReDial(serviceID string, config *tls.Config) *tls.Conn {
	reDial := 0
	for ok := true; ok; ok = reDial < 5 {
		conn, err := tls.Dial("tcp", serviceID, config)
		reDial++
		if err != nil {
			fmt.Println("Could not establish connection. Retrying in 5 seconds....")
			time.Sleep(time.Second * 5)
			continue
		}
		log.Println("Connected to: ", strings.Split(conn.RemoteAddr().String(), ":")[0])
		state := conn.ConnectionState()
		for _, v := range state.PeerCertificates {
			fmt.Println(x509.MarshalPKIXPublicKey(v.PublicKey))
			fmt.Println(v.Subject)
		}

		log.Println("client: handshake: ", state.HandshakeComplete)
		log.Println("client: mutual: ", state.NegotiatedProtocolIsMutual)
		return conn

	}
	fmt.Println("Could not reach server. Exiting....")
	os.Exit(1)
	return nil //will never reach this
}

func main() {
	err := godotenv.Load()
	if err != nil {
		fmt.Print("Error loading .env file")
		return
	}
	arguments := os.Args
	if len(arguments) == 1 {
		fmt.Println("Please provide host:port")
		return
	}

	genCert(os.Getenv("SSLCERTGENEMAIL_CLIENT"))
	cert, err := tls.LoadX509KeyPair("certs/client.pem", "certs/client.key")
	if err != nil {
		fmt.Println("Could not load SSL Certificate. Exiting...")
		return
	}
	config := tls.Config{Certificates: []tls.Certificate{cert}, InsecureSkipVerify: true}
	conn := dialReDial(arguments[1], &config)
	defer conn.Close()

	for {
		buffer := make([]byte, 1024)
		setReadDeadLine(conn)
		_, err := conn.Read(buffer)
		if err != nil {
			fmt.Println("Read Error. Checking status.")
			if err == io.EOF {
				fmt.Println("All commands ran successfully. Returning exit success.")
				os.Exit(0)
			}
		}

		sDec, _ := base64.StdEncoding.DecodeString(string(buffer[:]))
		//fmt.Println("$ " + string(sDec))
		resp := execInput(string(sDec))
		//fmt.Println(resp)
		time.Sleep(time.Second)
		encodedResp := base64.StdEncoding.EncodeToString([]byte(resp))
		setWriteDeadLine(conn)
		_, err = conn.Write([]byte(encodedResp))
		if err != nil {
			fmt.Println("Write Error. Exiting.")
			return
		}
		time.Sleep(time.Second)
		buffer = nil
	}
}
