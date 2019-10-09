package main

import (
	"errors"
	"io"
	"io/ioutil"
	"log"
	"time"

	"github.com/emersion/go-smtp"
)

const (
    HOST = "127.0.0.1"
    PORT = "47025"
    USERNAME = "sender"
    PASSWORD = "secret"
)

// The Backend implements SMTP server methods.
type Backend struct{}

// Login handles a login command with username and password.
func (bkd *Backend) Login(state *smtp.ConnectionState, username, password string) (smtp.Session, error) {
	if username != USERNAME || password != PASSWORD {
		return nil, errors.New("Invalid username or password")
	}
	return &Session{}, nil
}

// AnonymousLogin requires clients to authenticate using SMTP AUTH before sending emails
func (bkd *Backend) AnonymousLogin(state *smtp.ConnectionState) (smtp.Session, error) {
	return nil, smtp.ErrAuthRequired
}

// A Session is returned after successful login.
type Session struct{}

func (s *Session) Mail(from string) error {
	log.Println("Mail from:", from)
	return nil
}

func (s *Session) Rcpt(to string) error {
	log.Println("Rcpt to:", to)
	return nil
}

func (s *Session) Data(r io.Reader) error {
	if b, err := ioutil.ReadAll(r); err != nil {
		return err
	} else {
		log.Println("Data:", string(b))
	}
	return nil
}

func (s *Session) Reset() {}

func (s *Session) Logout() error {
	return nil
}

func main() {
	be := &Backend{}

	s := smtp.NewServer(be)

	s.Addr = ":" + PORT
	s.Domain = HOST
	s.ReadTimeout = 10 * time.Second
	s.WriteTimeout = 10 * time.Second
	s.MaxMessageBytes = 4 * 1024 * 1024
	s.MaxRecipients = 50
	s.AllowInsecureAuth = true

	log.Println("Starting server at", s.Addr + " ...")
	log.Println("Access as " + USERNAME + " with " + PASSWORD + " ...")
	if err := s.ListenAndServe(); err != nil {
		log.Fatal(err)
	}
}
