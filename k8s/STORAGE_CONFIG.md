# Storage Class Configuration

When applying PersistentVolumeClaims, set the `storageClassName` to match your cluster:

| Platform | Storage Class |
|---|---|
| DigitalOcean DOKS | `do-block-storage` |
| Minikube | `standard` |
| AWS EKS | `gp3` |
| GCP GKE | `standard` |
| Azure AKS | `azuredisk` |

The manifests in this repo default to `do-block-storage` (DigitalOcean).
To run on Minikube locally, change `storageClassName: do-block-storage` to `storageClassName: standard`
in `tracedata-db/pvc.yaml` and `tracedata-redis/pvc.yaml`.
