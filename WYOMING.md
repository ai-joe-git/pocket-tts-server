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

## References

- [Wyoming protocol](https://github.com/rhasspy/wyoming) (Rhasspy/OHF)
- [Home Assistant – Wyoming](https://www.home-assistant.io/integrations/wyoming/)
