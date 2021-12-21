# IBMS Kubernetes Kustomize overlay configuration

Declarative management of IBMS Kubernetes objects using Kustomize.

# How to use

Within an overlay directory, create a `.env` file to contain required secret
values in the format KEY=value (i.e. `overlays/uat/.env`). Required values:

    DATABASE_URL=value
    SECRET_KEY=value

Run `kubectl` with the `-k` flag to generate resources for a given overlay:

```bash
kubectl apply -k overlays/uat
```

# References:

* https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/
* https://github.com/kubernetes-sigs/kustomize
* https://github.com/kubernetes-sigs/kustomize/tree/master/examples
