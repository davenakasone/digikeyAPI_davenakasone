# DigiKey GitHub Examples & Open-Source Resources

This guide highlights community libraries, official SDKs, and reference code on GitHub for integrating with the DigiKey API.

---

## 1. Official Digi-Key GitHub Repositories

- **GitHub Organization:** [https://github.com/Digi-Key](https://github.com/Digi-Key)
- **Official C# SDK / Client:** Official C# implementation examples for OAuth and API v3/v4 endpoints.
- **Official Java SDK / Client:** Official Java implementation examples for OAuth authentication and client requests.
- **KiCad-Push-to-DigiKey:** Integration example demonstrating pushing BOM items directly to DigiKey carts/lists.

---

## 2. Community Python Libraries & Code Examples

### Standard `digikey-api` Library
- **Repository:** [https://github.com/peeter123/digikey-api](https://github.com/peeter123/digikey-api)
- **PyPI Package:** `digikey-api`
- **Notes:** Popular community wrapper for Part Search.

### Python API v4 Compatible Forks
Because DigiKey updated their API to v4, several active community forks support v4 search endpoints and updated authentication:
- **`hurricaneJoef/digikey-api`**: [https://github.com/hurricaneJoef/digikey-api](https://github.com/hurricaneJoef/digikey-api)
  - Install via pip: `pip install git+https://github.com/hurricaneJoef/digikey-api.git`
- **`digikey-apiv4` (PyPI)**: [https://pypi.org/project/digikey-apiv4/](https://pypi.org/project/digikey-apiv4/)

---

## 3. C# / .NET Libraries

- **`issus/DigiKeyApi`**: [https://github.com/issus/DigiKeyApi](https://github.com/issus/DigiKeyApi)
  - Comprehensive C# client covering Product Information V4, taxonomy search, and token refresh handling.

---

## 4. Node.js / TypeScript Guidance

Currently, there is no active official Node.js package. The recommended pattern is:

1. Use **`axios`**, **`fetch`**, or **`ky`** for HTTP calls.
2. Obtain the OpenAPI/Swagger specification file from the [DigiKey Developer Portal](https://developer.digikey.com/).
3. Use **OpenAPI Generator** to generate strongly-typed TypeScript interfaces and API clients:
   ```bash
   npx @openapitools/openapi-generator-cli generate \
     -i path/to/digikey-v4-swagger.json \
     -g typescript-axios \
     -o ./src/generated/digikey
   ```

---

## 5. Quick Python Implementation Example (Custom Requests Wrapper)

```python
import requests

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

def get_access_token():
    url = "https://api.digikey.com/v1/oauth2/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def search_part(mpn, token):
    url = f"https://api.digikey.com/products/v4/search/{mpn}/keyword"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-DIGIKEY-Client-Id": CLIENT_ID,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    token = get_access_token()
    results = search_part("STM32F407VGT6", token)
    print(results)
```
