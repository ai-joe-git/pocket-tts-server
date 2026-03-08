# Wyoming protocol (Home Assistant)

The server can speak the **Wyoming** protocol in parallel with the HTTP API. That lets [Home Assistant](https://www.home-assistant.io/integrations/wyoming/) use Pocket TTS (and Piper) for local voice output.

## Enable Wyoming

In **`config.json`** set:

```json
{
  "wyoming": {
    "enabled": true,
    "host": "0.0.0.0",
    "port": 10300
  }
}
```

- **enabled** – turn the Wyoming TCP server on or off.
- **host** – bind address (`0.0.0.0` = all interfaces, so HA on another machine can connect).
- **port** – TCP port (default **10300**).

Restart the server. You should see:

```text
[INFO] Wyoming protocol (Home Assistant) listening on 0.0.0.0:10300
```

## Home Assistant setup

1. In Home Assistant go to **Settings → Devices & services → Add integration**.
2. Search for **Wyoming** and add it.
3. Add a **Wyoming server** and enter your Pocket TTS server:
   - **Host:** IP of the machine running this server (e.g. `192.168.1.10` or `localhost` if HA is on the same host).
   - **Port:** `10300` (or the port you set in config).

Home Assistant will connect over TCP and use the Wyoming protocol to list voices and request TTS. All Pocket TTS and Piper voices from this server are exposed as Wyoming TTS voices.

## Behaviour

- The Wyoming server runs in the **same process** as the HTTP API and starts/stops with it.
- It only listens when **`wyoming.enabled`** is `true`.
- **Voices:** All voices from `voices-pockettts/`, `voices-celebrities/`, and `voices-piper/` are advertised. The client can request a voice by name; if none is given, the first available voice is used.
- No extra Python packages are required; the protocol is implemented directly.

## Troubleshooting

**"Unknown error occurred" in Home Assistant**

1. **Check the server console** – With Wyoming enabled, you should see:
   - `[INFO] Wyoming protocol (Home Assistant) listening on 0.0.0.0:10300`
   - When HA connects: `Wyoming: client connected from <IP>:<port>` and `Wyoming: describe received` / `describe -> info sent`
   - If you never see "client connected", HA cannot reach the server (firewall, wrong host/port, or server not listening on the right interface).

2. **Reachability** – Home Assistant must be able to open a **TCP** connection to the machine running this server on the Wyoming port (default 10300). If HA is on another machine:
   - Use the server’s LAN IP (e.g. `192.168.1.10`), not `localhost`.
   - Ensure no firewall blocks incoming TCP on the Wyoming port (Windows Firewall, router, etc.).

3. **Port** – In the Wyoming integration, use the **same port** as in `config.json` (`wyoming.port`). If you changed it (e.g. to 10301), enter that port in HA.

4. **Restart** – Restart this server after changing `config.json`, then in HA remove and re-add the Wyoming server if the problem persists.

**TTS entity is grayed out / cannot select**

Home Assistant only enables a TTS entity if it supports the **language** of your HA profile (or the voice assistant). This server reports support for **English (`en`) and German (`de`)**. If your Home Assistant UI language is set to one of these, the entity should be selectable after a reload. If you use another language only, the entity can stay grayed out; in that case set the assistant’s language to English or German for this TTS, or we can add more language codes to the server.

## References

- [Wyoming protocol](https://github.com/rhasspy/wyoming) (Rhasspy/OHF)
- [Home Assistant – Wyoming](https://www.home-assistant.io/integrations/wyoming/)
