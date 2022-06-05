openssl ecparam -genkey -name prime256v1 -noout -out ec_private_device1.pem
openssl req -new -sha256 -key ec_private_device1.pem -out ec_cert_device1.csr -subj "// CN=unused-device"
openssl x509 -req -in ec_cert_device1.csr -CA ca_cert_registry.pem -CAkey ca_private_registry.pem -CAcreateserial -sha256 -out ec_cert_device1.pem
openssl ec -in ec_private_device1.pem -noout -text
read