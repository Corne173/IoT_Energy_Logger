# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# [START iot_gateway_demo]
import csv
import datetime
import logging
import os

# sys.path.append(os.path.join(os.path.dirname(__file__), "../..", "manager"))  # noqa
import cloudiot_mqtt_example  # noqa
import manager  # noqa


logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.CRITICAL)

cloud_region = "europe-west1"

topic_id = f"test-device-events-topic"

ca_cert_path = "resources/roots.pem"
log_path = "config_log.csv"
rsa_public_path = "resources/ec_public.pem"
rsa_private_path = "resources/ec_private.pem"

os.environ['GOOGLE_CLOUD_PROJECT'] = 'mqtt-352311'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../service_account.json'

if (
    "GOOGLE_CLOUD_PROJECT" not in os.environ
    or "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ
):
    print("You must set GCLOUD_PROJECT and GOOGLE_APPLICATION_CREDENTIALS")
    quit()

project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
service_account_json = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

pubsub_topic = "projects/{}/topics/{}".format(project_id, topic_id)
registry_id = "Test_registry"

base_url = "https://console.cloud.google.com/iot/locations/{}".format(cloud_region)
edit_template = "{}/registries/{}?project={}".format(base_url, "{}", "{}")

device_url_template = "{}/registries/{}/devices/{}?project={}".format(
    base_url, "{}", "{}", "{}"
)

mqtt_bridge_hostname = "mqtt.googleapis.com"
mqtt_bridge_port = 8883

num_messages = 1
jwt_exp_time = 20
listen_time = 10


if __name__ == "__main__":


    print("Running demo")

    gateway_id = "Test_gateway"
    device_id = "Tesssst_device"

    # [START iot_gateway_demo_create_registry]
    # print(f"Creating registry: {registry_id}")
    # manager.create_registry(
    #     service_account_json, project_id, cloud_region, pubsub_topic, registry_id
    # )
    # [END iot_gateway_demo_create_registry]

    # [START iot_gateway_demo_create_gateway]
    # print("Creating gateway: {}".format(gateway_id))
    # manager.create_gateway(
    #     service_account_json,
    #     project_id,
    #     cloud_region,
    #     registry_id,
    #     None,
    #     gateway_id,
    #     rsa_public_path,
    #     "ES256",
    # )
    # [END iot_gateway_demo_create_gateway]

    # [START iot_gateway_demo_create_bound_device]
    print("Creating device to bind: {}".format(device_id))
    manager.create_es256_device(
        service_account_json,
        project_id,
        cloud_region,
        registry_id,
        device_id,
        rsa_public_path,
    )
    # [END iot_gateway_demo_create_bound_device]

    # [START iot_gateway_demo_bind_device]
    print("Binding device")
    manager.bind_device_to_gateway(
        service_account_json,
        project_id,
        cloud_region,
        registry_id,
        device_id,
        gateway_id,
    )
    # [END iot_gateway_demo_bind_device]

    # [START iot_gateway_demo_listen]
    print("Listening for messages for {listen_time} seconds")
    print("Try setting configuration in: ")
    print(f"\t{registry_id}\t{project_id}")
    try:
        input("Press enter to continue")
    except SyntaxError:
        pass

    def log_callback(client):
        def log_on_message(unused_client, unused_userdata, message):
            print(f"Message received: {message.payload}")
            if not os.path.exists(log_path):
                with open(log_path, "w") as csvfile:
                    logwriter = csv.writer(csvfile, dialect="excel")
                    logwriter.writerow(["time", "topic", "data"])

            with open(log_path, "a") as csvfile:
                logwriter = csv.writer(csvfile, dialect="excel")
                logwriter.writerow(
                    [
                        datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
                        message.topic,
                        message.payload,
                    ]
                )

        client.on_message = log_on_message

    cloudiot_mqtt_example.listen_for_messages(
        service_account_json,
        project_id,
        cloud_region,
        registry_id,
        device_id,
        gateway_id,
        num_messages,
        rsa_private_path,
        "RS256",
        ca_cert_path,
        mqtt_bridge_hostname,
        mqtt_bridge_port,
        jwt_exp_time,
        listen_time,
        log_callback,
    )
    # [END iot_gateway_demo_listen]

    # [START iot_gateway_demo_publish]
    print("Publishing messages demo")
    print(f"Publishing: {num_messages} messages")
    cloudiot_mqtt_example.send_data_from_bound_device(
        service_account_json,
        project_id,
        cloud_region,
        registry_id,
        device_id,
        gateway_id,
        num_messages,
        rsa_private_path,
        "RS256",
        ca_cert_path,
        mqtt_bridge_hostname,
        mqtt_bridge_port,
        jwt_exp_time,
        "Hello from gateway_demo.py",
    )

    print("You can read the state messages for your device at this URL:")
    print("\t{}".format(device_url_template).format(registry_id, device_id, project_id))
    try:
        input("Press enter to continue after reading the messages.")
    except SyntaxError:
        pass
    # [END iot_gateway_demo_publish]

    # [START iot_gateway_demo_cleanup]
    # Clean up
    manager.unbind_device_from_gateway(
        service_account_json,
        project_id,
        cloud_region,
        registry_id,
        device_id,
        gateway_id,
    )
    manager.delete_device(
        service_account_json, project_id, cloud_region, registry_id, device_id
    )
    manager.delete_device(
        service_account_json, project_id, cloud_region, registry_id, gateway_id
    )
    manager.delete_registry(service_account_json, project_id, cloud_region, registry_id)
    # [END iot_gateway_demo_cleanup]

# [END iot_gateway_demo]
