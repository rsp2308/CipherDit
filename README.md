# CipherDit – Encrypted Wireless Morse Communication System

CipherDit is a low-cost, infrastructure-free wireless communication system that combines **Morse code input, RF transmission, substitution-cipher encryption, and a Python receiver GUI**.

The system uses two Arduino Uno boards with **NRF24L01+ PA/LNA 2.4 GHz transceiver modules**. A transmitter converts button-based Morse input into characters, encrypts them using a fixed substitution cipher, and sends them wirelessly. The receiver forwards the encrypted data to a Python desktop application over USB serial, where it is decrypted and displayed along with live RSSI information.

## Features

- Wireless Morse communication over the **2.4 GHz ISM band**
- Morse input using dedicated **dot and dash push buttons**
- Fixed-key **monoalphabetic substitution cipher**
- NRF24L01+ PA/LNA RF communication
- Real-time **RSSI monitoring and graphing**
- Python desktop GUI for encrypted/decrypted message display
- Automatic **SOS detection and alert**
- Serial communication between Arduino and Python at **115200 baud**

## System Architecture

```text
┌─────────────────────┐
│   TRANSMITTER       │
│                     │
│ Push Buttons        │
│    ↓                │
│ Morse Encoding      │
│    ↓                │
│ Substitution Cipher │
│    ↓                │
│ Arduino Uno         │
│    ↓                │
│ NRF24L01+ PA/LNA    │
└──────────┬──────────┘
           │ 2.4 GHz RF
           ▼
┌─────────────────────┐
│     RECEIVER        │
│                     │
│ NRF24L01+ PA/LNA    │
│    ↓                │
│ Arduino Uno         │
│    ↓ USB Serial     │
└──────────┬──────────┘
           │ 115200 baud
           ▼
┌─────────────────────┐
│   CipherDit GUI     │
│                     │
│ Reverse Cipher      │
│ RSSI Visualization  │
│ Message Display     │
│ SOS Detection       │
└─────────────────────┘
```

## Hardware

| Component | Quantity | Purpose |
|---|---:|---|
| Arduino Uno | 2 | Transmitter and receiver controllers |
| NRF24L01+ PA/LNA | 2 | 2.4 GHz wireless communication |
| Push Buttons | 2 | Dot and dash Morse input |
| Active Buzzer | 1 | Audio feedback for Morse input |
| Blue LED | 1 | Receiver-side Morse indication |
| 100 µF Capacitor | 2 | NRF24L01+ power-spike filtering |
| 220 Ω Resistor | 1 | LED current limiting |
| Breadboard & Jumpers | — | Prototyping |
| USB Cable | 2 | Arduino-to-PC serial connection |

## Pin Configuration

| NRF24L01+ Signal | Arduino Pin |
|---|---|
| CE | D9 |
| CSN | D10 |
| MOSI | D11 |
| MISO | D12 |
| SCK | D13 |
| VCC | 3.3V |

Additional transmitter/receiver connections:

- Dot button → D2
- Dash button → D3
- Buzzer → D6
- Blue LED → D5 through 220 Ω resistor

> **Important:** The NRF24L01+ module is powered from **3.3V, not 5V**. A 100 µF capacitor is used across VCC and GND to reduce RF power-related instability.

## RF Configuration

- Frequency: **2515 MHz**
- RF Channel: **115**
- Data Rate: **250 Kbps**
- Serial Baud Rate: **115200**
- Packet payload: **1 character**

The 250 Kbps setting was selected to improve link reliability compared with higher data rates. The report records approximately **15% packet loss at 1 Mbps**, dropping to near zero at 250 Kbps during testing.

## Software Stack

- **Arduino IDE**
- **C++ / Arduino firmware**
- **RF24 library**
- **Python**
- **CustomTkinter**
- **pySerial**
- **Matplotlib**

## How It Works

1. The user presses the dot or dash button on the transmitter.
2. The Arduino accumulates the Morse sequence.
3. After approximately 2 seconds without another input, the sequence is decoded into a character.
4. The character is transformed using the fixed substitution cipher.
5. The encrypted character is transmitted through the NRF24L01+.
6. The receiver Arduino receives the RF packet and sends it to the PC over USB serial.
7. The Python GUI reverses the cipher and displays the plaintext.
8. RSSI and link statistics are updated in real time.
9. If `SOS` is detected in the decrypted message, the GUI raises an emergency alert.

## Performance

| Metric | Result |
|---|---:|
| RF Frequency | 2515 MHz |
| Data Rate | 250 Kbps |
| End-to-End Latency | < 50 ms |
| Indoor Range | ~100 m |
| Open-Air Range | Up to 1,000 m with PA/LNA |
| Power per Node | ~50 mA @ 3.3V |
| Serial Baud Rate | 115200 baud |
| Packet Size | 1 character |
| SOS Detection | Automatic |

## Project Images

### CipherDit Receiver GUI

![CipherDit GUI](images/cipherdit-gui.png)

The receiver application displays the encrypted incoming stream, decrypted message, live RSSI graph, and link statistics.

### Hardware Setup

<img width="737" height="693" alt="image" src="https://github.com/user-attachments/assets/bb949a0c-a096-44d3-8b94-feca84a546b7" />


Arduino Uno connected to the NRF24L01+ PA/LNA module through the SPI interface, with breadboard prototyping and USB serial connection.

### Arduino Serial Monitor

![Arduino Serial Monitor](images/serial-monitor.png)

Arduino IDE Serial Monitor output showing transmitter/receiver status and received encrypted characters.

## Engineering Challenges

- **NRF24L01+ power instability:** addressed with 100 µF capacitors across the RF module supply.
- **Wi-Fi interference:** reduced by selecting RF channel 115.
- **SPI synchronization:** improved using stabilization delays and stable CSN handling.
- **Arduino SRAM fragmentation:** reduced by replacing dynamic `String` usage with character arrays.
- **Packet loss:** improved by switching from 1 Mbps to 250 Kbps.

## Future Scope

- AES-128 encryption
- 16×2 I2C LCD for standalone operation
- Frequency hopping
- Bidirectional communication with acknowledgements
- Multi-node mesh networking
- SD-card message logging
- Android application integration



> This README is based on the project report and its documented hardware setup, software architecture, methodology, images, and measured results.
