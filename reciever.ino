#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9,10);

const byte address[6] = "00001";

// USING BUILT-IN LED
const int LED_PIN = 7;

// ================= MORSE TABLE =================
String getMorse(char letter) {

  if(letter=='A') return "01";
  if(letter=='B') return "1000";
  if(letter=='C') return "1010";
  if(letter=='D') return "100";
  if(letter=='E') return "0";
  if(letter=='F') return "0010";
  if(letter=='G') return "110";
  if(letter=='H') return "0000";
  if(letter=='I') return "00";
  if(letter=='J') return "0111";
  if(letter=='K') return "101";
  if(letter=='L') return "0100";
  if(letter=='M') return "11";
  if(letter=='N') return "10";
  if(letter=='O') return "111";
  if(letter=='P') return "0110";
  if(letter=='Q') return "1101";
  if(letter=='R') return "010";
  if(letter=='S') return "000";
  if(letter=='T') return "1";
  if(letter=='U') return "001";
  if(letter=='V') return "0001";
  if(letter=='W') return "011";
  if(letter=='X') return "1001";
  if(letter=='Y') return "1011";
  if(letter=='Z') return "1100";

  return "";
}

// ================= LED MORSE =================
void blinkMorse(String code) {

  for(int i=0; i<code.length(); i++) {

    // DOT
    if(code[i]=='0') {

      digitalWrite(LED_PIN,HIGH);

      delay(120);

      digitalWrite(LED_PIN,LOW);

      delay(120);
    }

    // DASH
    else if(code[i]=='1') {

      digitalWrite(LED_PIN,HIGH);

      delay(400);

      digitalWrite(LED_PIN,LOW);

      delay(120);
    }
  }
}

void setup() {

  pinMode(LED_PIN, OUTPUT);

  digitalWrite(LED_PIN,LOW);

  Serial.begin(115200);

  delay(2000);

  radio.begin();

  radio.setPALevel(RF24_PA_MIN);

  radio.setDataRate(RF24_250KBPS);

  radio.setChannel(115);

  radio.openReadingPipe(0,address);

  radio.startListening();

  Serial.println("RX Ready");
}

void loop() {

  if(radio.available()) {

    char text[32] = "";

    radio.read(&text,sizeof(text));

    char letter = text[0];

    // Serial.print("Received: ");

    Serial.print(letter);

    String morse = getMorse(letter);

    blinkMorse(morse);
  }
}
