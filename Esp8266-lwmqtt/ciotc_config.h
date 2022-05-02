// This file contains your configuration used to connect to Cloud IoT Core

// WIFI
const char* ssid = "Your Wifi SSID";
const char* password = "Your WIFI passwaord";

// Cloud iot details.
const char* project_id = "Check your Google Cloud account for details";
const char* location = "";
const char* registry_id = "";
const char* device_id = "";

// Configuration for NTP
const char* ntp_primary = "time.google.com";
const char* ntp_secondary = "pool.ntp.org";

// To get the private key run (where private-key.pem is the ec private key
// used to create the certificate uploaded to google cloud iot):
// openssl ec -in <private-key.pem> -noout -text
// and copy priv: part.
// The key length should be exactly the same as the key length bellow (32 pairs
// of hex digits). If it's bigger and it starts with "00:" delete the "00:". If
// it's smaller add "00:" to the start. If it's too big or too small something
// is probably wrong with your key.
const unsigned char private_key[] = {0xc4,0x61,0x0e,0xe4,0xcf,0x32,0x1f,0x1c,0x53,0xd4,0xe4,0x46,0x55,0xa9,0xec,0x78,0x15,0xef,0xe3,0xf3,0x23,0x60,0x15,0xc5,0xfd,0x66,0x07,0xe8,0xd4,0xf1,0x3d,0xed};

// Time (seconds) to expire token += 20 minutes for drift
const int jwt_exp_secs = 3600; // Maximum 24H (3600*24)

// Certificates for SSL on the LTS server
const char* primary_ca = "-----BEGIN CERTIFICATE-----\n"
    "MIIBxTCCAWugAwIBAgINAfD3nVndblD3QnNxUDAKBggqhkjOPQQDAjBEMQswCQYD\n"
    "VQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2VzIExMQzERMA8G\n"
    "A1UEAxMIR1RTIExUU1IwHhcNMTgxMTAxMDAwMDQyWhcNNDIxMTAxMDAwMDQyWjBE\n"
    "MQswCQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2VzIExM\n"
    "QzERMA8GA1UEAxMIR1RTIExUU1IwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAATN\n"
    "8YyO2u+yCQoZdwAkUNv5c3dokfULfrA6QJgFV2XMuENtQZIG5HUOS6jFn8f0ySlV\n"
    "eORCxqFyjDJyRn86d+Iko0IwQDAOBgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUw\n"
    "AwEB/zAdBgNVHQ4EFgQUPv7/zFLrvzQ+PfNA0OQlsV+4u1IwCgYIKoZIzj0EAwID\n"
    "SAAwRQIhAPKuf/VtBHqGw3TUwUIq7TfaExp3bH7bjCBmVXJupT9FAiBr0SmCtsuk\n"
    "miGgpajjf/gFigGM34F9021bCWs1MbL0SA==\n"
    "-----END CERTIFICATE-----\n";

const char* backup_ca = "-----BEGIN CERTIFICATE-----\n"
    "MIIB4TCCAYegAwIBAgIRKjikHJYKBN5CsiilC+g0mAIwCgYIKoZIzj0EAwIwUDEk\n"
    "MCIGA1UECxMbR2xvYmFsU2lnbiBFQ0MgUm9vdCBDQSAtIFI0MRMwEQYDVQQKEwpH\n"
    "bG9iYWxTaWduMRMwEQYDVQQDEwpHbG9iYWxTaWduMB4XDTEyMTExMzAwMDAwMFoX\n"
    "DTM4MDExOTAzMTQwN1owUDEkMCIGA1UECxMbR2xvYmFsU2lnbiBFQ0MgUm9vdCBD\n"
    "QSAtIFI0MRMwEQYDVQQKEwpHbG9iYWxTaWduMRMwEQYDVQQDEwpHbG9iYWxTaWdu\n"
    "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEuMZ5049sJQ6fLjkZHAOkrprlOQcJ\n"
    "FspjsbmG+IpXwVfOQvpzofdlQv8ewQCybnMO/8ch5RikqtlxP6jUuc6MHaNCMEAw\n"
    "DgYDVR0PAQH/BAQDAgEGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFFSwe61F\n"
    "uOJAf/sKbvu+M8k8o4TVMAoGCCqGSM49BAMCA0gAMEUCIQDckqGgE6bPA7DmxCGX\n"
    "kPoUVy0D7O48027KqGx2vKLeuwIgJ6iFJzWbVsaj8kfSt24bAgAXqmemFZHe+pTs\n"
    "ewv4n4Q=\n"
    "-----END CERTIFICATE-----\n";

// In case we ever need extra topics
const int ex_num_topics = 0;
const char* ex_topics[ex_num_topics];
//const int ex_num_topics = 1;
//const char* ex_topics[ex_num_topics] = {
//  "/devices/my-device/tbd/#"
//};
