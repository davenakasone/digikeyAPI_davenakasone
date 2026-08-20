# DigiKey OAuth 2.0 Authentication Guide

DigiKey APIs rely on **OAuth 2.0** for security. Access tokens are required for all API calls.

---

## 1. Prerequisites & Credential Storage

1. **Developer Portal App:** Register your app at [developer.digikey.com](https://developer.digikey.com/) and subscribe it to **Product Information V4** and **Reference APIs**.
2. **Retrieve Credentials:** Obtain your **Client ID** (`client_id`) and **Client Secret** (`client_secret`).
3. **Storage & Configuration:**
   - Environment Variable: `DIGIKEY_ENV_PATH` pointing to your `.env` vault
   - Direct Environment Variables: `DIGIKEY_CLIENT_ID`, `DIGIKEY_CLIENT_SECRET`
   - Local Fallback: `.env` file in the project root (gitignored)

---

## 2. Authentication Flows

### Flow A: 2-Legged OAuth (Client Credentials Grant) — *Default & Recommended*

* **Best For:** Automated part lookup, catalog search, pricing checks, parametric data, and datasheets.
* **Benefits:** Requires **zero** manual browser logins, interactive callbacks, or user prompts.
* **Token Endpoint:** `https://api.digikey.com/v1/oauth2/token`
* **HTTP Method:** `POST`
* **Content-Type:** `application/x-www-form-urlencoded`
* **Token Lifetime:** Typically 600 seconds (10 minutes) or 1800 seconds (30 minutes).

#### Request Payload:
```http
POST /v1/oauth2/token HTTP/1.1
Host: api.digikey.com
Content-Type: application/x-www-form-urlencoded

client_id=<YOUR_CLIENT_ID>&client_secret=<YOUR_CLIENT_SECRET>&grant_type=client_credentials
```

#### Response Example:
```json
{
  "access_token": "a0LaC9ZgGAUdXtCiQHCOLSCpoG9A",
  "expires_in": 599,
  "token_type": "Bearer"
}
```

---

### Flow B: 3-Legged OAuth (Authorization Code Grant)

* **Best For:** User-specific account actions (e.g., custom user pricing quotes, saved lists, account order management).
* **Requirements:** User authorization in browser, redirect URL, authorization code handling.

#### Step 1: Redirect User to Authorization Page
```http
GET https://api.digikey.com/v1/oauth2/authorize?response_type=code&client_id=<YOUR_CLIENT_ID>&redirect_uri=https://localhost
```

#### Step 2: Exchange Authorization Code for Tokens
> ⚠️ **Note:** Authorization codes expire in ~60 seconds and are strictly single-use.

```bash
curl -X POST "https://api.digikey.com/v1/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "code=AUTHORIZATION_CODE_FROM_REDIRECT" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=https://localhost"
```

#### Response Example:
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "rF81kZ...",
  "token_type": "Bearer",
  "expires_in": 1800
}
```

#### Step 3: Refreshing an Expired Access Token
When an access token expires:

```bash
curl -X POST "https://api.digikey.com/v1/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "grant_type=refresh_token"
```

---

## 3. Required Headers for API Calls

For all DigiKey v4 REST endpoints, **both** headers are strictly required:

```http
Authorization: Bearer <access_token>
X-DIGIKEY-Client-Id: <client_id>
Content-Type: application/json
Accept: application/json
```

---

## 4. Troubleshooting & Gotchas Summary

1. **Missing `X-DIGIKEY-Client-Id`:** Omitting this header causes `401 Unauthorized` or `403 Forbidden` even with a valid Bearer token.
2. **Sandbox Network Policy:** `403 Request to POST /v1/oauth2/token on api.digikey.com not allowed by policy` indicates local environment egress/sandbox blocking, not DigiKey rejecting the request.
3. **Single-Use Auth Code:** Reusing or delaying authorization code exchange causes `400 Bad Request: Invalid authCode`.
4. **Token Caching:** Client implementations must track `expires_in` / `expires_at` and request fresh tokens 60 seconds before expiration.
