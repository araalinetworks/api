package template

import (
	"log"
)

type Config struct {
	SSLEMAIL    string
	CLIENTLOG   *log.Logger
	HOST        string
	PORT        string
	LOGNAME     string
	MAXLOGSTORE int
}

type User struct {
	NAME     string `json:"name"`
	EMAIL    string `json:"email"`
	PASSWORD []byte `json:"pwd"`
}
type Msg struct {
	MESSAGE string `json:"message"`
}

type LogSuccess struct {
	TOKEN   string `json:"token"`
	MESSAGE string `json:"message"`
}

type UserLinks struct{
	EMAIL string `json:"email"`
	TOKEN string `json:"token"`
	LOGID int  `json:"logid"`
	
}

type LoggedUser struct {
	EMAIL string `json:"email"`
	TOKEN string `json:"token"`
}

type LoginUser struct {
	EMAIL    string `json:"email"`
	PASSWORD []byte `json:"pwd"`
}
