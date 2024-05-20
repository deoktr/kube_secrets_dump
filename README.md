# kube_secrets_dump

Dump and decode Kubernetes secrets.

This can be usefull during red team engagment if you come across a Kubernetes server and want to download every secret from it.

The output format is JSON.

## Requirements

You need to have access to the target Kubernetes instance and be authenticated to it.

## Usage

Run:

```bash
python3 main.py
```

You can also specify the namespace.

## License

[MIT](./LICENSE)
