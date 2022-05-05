package note

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"github.com/GermanBogatov/notes_service/app/internal/apperror"
	"github.com/GermanBogatov/notes_service/app/pkg/logging"
	"github.com/julienschmidt/httprouter"
	"io"
	"net/http"
)

const (
	notesURL   = "/api/notes"
	noteURL    = "/api/notes/:uuid"
	headersURL = "/api/headers"
	constkey   = "2a7d6efd68a1b0e8fbce78c964ca4efe6bb7e3aaca413f664b54b50301e58f5b"
)

type Handler struct {
	Logger      logging.Logger
	NoteService Service
}

func (h *Handler) Register(router *httprouter.Router) {
	router.HandlerFunc(http.MethodGet, headersURL, apperror.Middleware(h.GetHeadersByUser))
	router.HandlerFunc(http.MethodGet, noteURL, apperror.Middleware(h.GetNote))
	router.HandlerFunc(http.MethodGet, notesURL, apperror.Middleware(h.GetNotesByUser))
	router.HandlerFunc(http.MethodPost, notesURL, apperror.Middleware(h.CreateNote))
	router.HandlerFunc(http.MethodPatch, noteURL, apperror.Middleware(h.PartiallyUpdateNote))
	router.HandlerFunc(http.MethodDelete, noteURL, apperror.Middleware(h.DeleteNote))
}

func (h *Handler) GetHeadersByUser(w http.ResponseWriter, r *http.Request) error {
	h.Logger.Info("GET HEADERS BY USER")
	w.Header().Set("Content-Type", "application/json")
	h.Logger.Debug("get user_uuid from URL")
	userUUID := r.URL.Query().Get("user_uuid")
	if userUUID == "" {
		return apperror.BadRequestError("user_uuid query parameter is required and must be a comma separated integers")
	}
	notes, err := h.NoteService.GetHeadersByUserUUID(r.Context(), userUUID)
	if err != nil {
		return err
	}
	fmt.Println("notes: ", notes)
	notesBytes, err := json.Marshal(notes)
	if err != nil {
		return err
	}
	fmt.Println("notesBytes: ", notesBytes)
	w.WriteHeader(http.StatusOK)
	w.Write(notesBytes)

	return nil
}

func (h *Handler) GetNote(w http.ResponseWriter, r *http.Request) error {
	h.Logger.Info("GET NOTE")
	w.Header().Set("Content-Type", "application/json")

	h.Logger.Debug("get uuid from context")
	params := r.Context().Value(httprouter.ParamsKey).(httprouter.Params)

	noteUUID := params.ByName("uuid")
	if noteUUID == "" {
		return apperror.BadRequestError("uuid query parameter is required and must be a comma separated integers")
	}
	note, err := h.NoteService.GetOne(r.Context(), noteUUID)
	/*decryptedAES := decryptAES256(note.Body, constkey)
	note.Body = decryptedAES*/
	if err != nil {
		return err
	}
	noteBytes, err := json.Marshal(note)
	if err != nil {
		return err
	}

	w.WriteHeader(http.StatusOK)
	w.Write(noteBytes)

	return nil
}

func (h *Handler) GetNotesByUser(w http.ResponseWriter, r *http.Request) error {
	h.Logger.Info("GET NOTES BY USER")
	w.Header().Set("Content-Type", "application/json")
	h.Logger.Debug("get user_uuid from URL")
	userUUID := r.URL.Query().Get("user_uuid")
	if userUUID == "" {
		return apperror.BadRequestError("user_uuid query parameter is required and must be a comma separated integers")
	}

	notes, err := h.NoteService.GetByUserUUID(r.Context(), userUUID)
	if err != nil {
		return err
	}

	notesBytes, err := json.Marshal(notes)
	if err != nil {
		return err
	}
	w.WriteHeader(http.StatusOK)
	w.Write(notesBytes)

	return nil
}

func (h *Handler) CreateNote(w http.ResponseWriter, r *http.Request) error {
	h.Logger.Info("CREATE NOTE")
	w.Header().Set("Content-Type", "application/json")

	h.Logger.Debug("decode create tag dto")
	var dto CreateNoteDTO
	defer r.Body.Close()
	if err := json.NewDecoder(r.Body).Decode(&dto); err != nil {
		return apperror.BadRequestError("invalid data")
	}
	/*encryptedAES := encryptAES256(dto.Body, constkey)
	fmt.Printf("encrypted AES: %s\n", encryptedAES)
	dto.Body = encryptedAES*/
	noteUUID, err := h.NoteService.Create(r.Context(), dto)
	if err != nil {
		return err
	}
	w.Header().Set("Location", fmt.Sprintf("%s/%s", notesURL, noteUUID))
	w.WriteHeader(http.StatusCreated)

	return nil
}

func (h *Handler) PartiallyUpdateNote(w http.ResponseWriter, r *http.Request) error {
	h.Logger.Info("PARTIALLY UPDATE NOTE")
	w.Header().Set("Content-Type", "application/json")

	h.Logger.Debug("get uuid from context")
	params := r.Context().Value(httprouter.ParamsKey).(httprouter.Params)
	noteUUID := params.ByName("uuid")
	if noteUUID == "" {
		return apperror.BadRequestError("uuid query parameter is required and must be a comma separated integers")
	}

	h.Logger.Debug("decode update tag dto")
	var dto UpdateNoteDTO
	defer r.Body.Close()
	if err := json.NewDecoder(r.Body).Decode(&dto); err != nil {
		return apperror.BadRequestError("invalid data")
	}

	dto.UUID = noteUUID

	err := h.NoteService.Update(r.Context(), dto)
	if err != nil {
		return err
	}
	w.WriteHeader(http.StatusNoContent)

	return nil
}

func (h *Handler) DeleteNote(w http.ResponseWriter, r *http.Request) error {
	h.Logger.Info("DELETE NOTE")
	w.Header().Set("Content-Type", "application/json")

	h.Logger.Debug("get uuid from context")
	params := r.Context().Value(httprouter.ParamsKey).(httprouter.Params)
	noteUUID := params.ByName("uuid")
	if noteUUID == "" {
		return apperror.BadRequestError("uuid query parameter is required and must be a comma separated integers")
	}

	err := h.NoteService.Delete(r.Context(), noteUUID)
	if err != nil {
		return err
	}
	w.WriteHeader(http.StatusNoContent)

	return nil
}

func encryptAES256(stringToEncrypt string, keyString string) (encryptedString string) {

	key, _ := hex.DecodeString(keyString)
	plaintext := []byte(stringToEncrypt)

	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err.Error())
	}

	aesGCM, err := cipher.NewGCM(block)
	if err != nil {
		panic(err.Error())
	}

	nonce := make([]byte, aesGCM.NonceSize())
	if _, err = io.ReadFull(rand.Reader, nonce); err != nil {
		panic(err.Error())
	}
	ciphertext := aesGCM.Seal(nonce, nonce, plaintext, nil)
	return fmt.Sprintf("%x", ciphertext)
}

func decryptAES256(encryptedString string, keyString string) (decryptedString string) {

	key, _ := hex.DecodeString(keyString)
	enc, _ := hex.DecodeString(encryptedString)
	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err.Error())
	}
	aesGCM, err := cipher.NewGCM(block)
	if err != nil {
		panic(err.Error())
	}
	nonceSize := aesGCM.NonceSize()
	nonce, ciphertext := enc[:nonceSize], enc[nonceSize:]
	plaintext, err := aesGCM.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		panic(err.Error())
	}
	return fmt.Sprintf("%s", plaintext)
}
