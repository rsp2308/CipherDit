#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(9,10);

const byte address[6] = "00001";

const int DOT_BTN = 2;
const int DASH_BTN = 3;
const int BUZZER = 6;

String morse = "";

unsigned long lastPress = 0;
const int letterGap = 2000;

String decodeMorse(String code) {

  if(code=="01") return "A";
  if(code=="1000") return "B";
  if(code=="1010") return "C";
  if(code=="100") return "D";
  if(code=="0") return "E";
  if(code=="0010") return "F";
  if(code=="110") return "G";
  if(code=="0000") return "H";
  if(code=="00") return "I";
  if(code=="0111") return "J";
  if(code=="101") return "K";
  if(code=="0100") return "L";
  if(code=="11") return "M";
  if(code=="10") return "N";
  if(code=="111") return "O";
  if(code=="0110") return "P";
  if(code=="1101") return "Q";
  if(code=="010") return "R";
  if(code=="000") return "S";
  if(code=="1") return "T";
  if(code=="001") return "U";
  if(code=="0001") return "V";
  if(code=="011") return "W";
  if(code=="1001") return "X";
  if(code=="1011") return "Y";
  if(code=="1100") return "Z";

  return "?";
}

void setup() {

  pinMode(DOT_BTN, INPUT_PULLUP);
  pinMode(DASH_BTN, INPUT_PULLUP);

  pinMode(BUZZER, OUTPUT);

  Serial.begin(115200);

  delay(2000);

  radio.begin();

  radio.setPALevel(RF24_PA_MIN);
  radio.setDataRate(RF24_250KBPS);

  radio.openWritingPipe(address);

  radio.stopListening();

  Serial.println("TX Ready");
}

void loop() {

  // DOT
  if(digitalRead(DOT_BTN)==LOW) {

    morse += "0";

    tone(BUZZER,1000,80);

    lastPress = millis();

    delay(300);
  }

  // DASH
  if(digitalRead(DASH_BTN)==LOW) {

    morse += "1";

    tone(BUZZER,1000,300);

    lastPress = millis();

    delay(300);
  }

  // Decode after silence
  if(morse.length()>0 && millis()-lastPress > letterGap) {

    String letter = decodeMorse(morse);

    Serial.print("Sent Letter: ");
    Serial.println(letter);

    char text[2];

    text[0] = letter.charAt(0);
    text[1] = '\0';

    radio.write(&text,sizeof(text));

    morse = "";

    delay(500);
  }
}
