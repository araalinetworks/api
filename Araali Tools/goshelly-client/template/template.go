package template

import "log"



type Config struct {
	SSLEMAIL  string
	CLIENTLOG *log.Logger
	HOST      string
	PORT      string
	LOGNAME   string
	MAXLOGSTORE int
}