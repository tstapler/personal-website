# ArgoCD Operations

## Accessing the ArgoCD UI

To access the ArgoCD dashboard, you will need to port-forward the ArgoCD server service to your local machine.

### 1. Port Forwarding

Run the following command in your terminal:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

### 2. Access the UI

Open your browser and navigate to:
[https://localhost:8080](https://localhost:8080)

*Note: You may see a TLS/SSL warning because the server uses a self-signed certificate. It is safe to proceed.*

### 3. Login Credentials

- **Username**: `admin`
- **Password**: Retrieve the initial admin password using the following command:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

Copy the output and use it to log in.
