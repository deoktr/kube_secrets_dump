#!/usr/bin/env python
import base64
import json
import logging
import subprocess


def get_secret_list(global_namespace=None):
    command = ["kubectl", "get", "secrets", "--all-namespaces"]
    if global_namespace:
        command = ["kubectl", "get", "secrets", "--namespace", global_namespace]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout.decode()
    # [1:-1] removes `""`
    lines = result.split("\n")[1:-1]
    secrets = []
    for line in lines:
        if global_namespace:
            namespace = global_namespace
            name, type, data, age = line.split()
        else:
            namespace, name, type, data, age = line.split()
        secrets.append(
            {
                "namespace": namespace,
                "name": name,
                "type": type,
                "data": data,
                "age": age,
            }
        )
    return secrets


def read_secret(secret_name, namespace):
    command = [
        "kubectl",
        "get",
        "secrets",
        "--namespace",
        namespace,
        secret_name,
        "-o",
        'jsonpath="{.data}"',
    ]
    # [1:-1] removes `""`
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout.decode()[1:-1]

    if len(result) == 0:
        return None
    try:
        j = json.loads(result)
        for key, value in j.items():
            decoded_value = base64.b64decode(value).decode()
            # try to load the value of the key, sometimes keys contain JSON,
            # it's useful to load them so they are available has dict
            try:
                decoded_value = json.loads(decoded_value)
            except Exception:
                pass
            j.update({key: decoded_value})
        return j
    except Exception:
        print("[-] error trying to decode {} from {}".format(secret_name, namespace))
        return result


def run(namespace=None):
    msg = "[*] looking for kubernetes secrets"
    if namespace:
        msg += " in namespace: {}".format(namespace)
    logging.debug(msg)
    secret_list = get_secret_list(namespace)
    len_secret = len(secret_list)
    logging.info("[+] found {} secrets".format(len_secret))
    n = 0
    for secret in secret_list:
        logging.debug("[*] checking: {} ({}/{})".format(secret["name"], n, len_secret))
        secret_name = secret["name"]
        namespace = secret["namespace"]
        secret_values = read_secret(secret_name=secret_name, namespace=namespace)
        secret.update({"values": secret_values})
        n += 1
    logging.info("[+] successfully collected {} secrets".format(len_secret))
    return secret_list


if __name__ == "__main__":
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format="%(message)s")

    namespace = None
    if len(sys.argv) >= 2:
        namespace = sys.argv[1]

    secret_list = run(namespace=namespace)

    output_file = "out.json"
    out_file = open(output_file, "w")
    json.dump(secret_list, out_file, indent=2)
    out_file.close()
    logging.info("[+] output written to '{}'".format(output_file))
