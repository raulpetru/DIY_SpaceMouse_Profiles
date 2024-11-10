# Description
DIY SpaceMouse Profiles will provide a user interface for the values provided by the Space Mouse firmware.

The firmware provided in this repository is modified to send through serial information to build the UI:
<details>
  <summary>Show code</summary>

```c++
void return_ui() {
    const char * ui_values=
    "name=TRANSX_SENSITIVITY;type=slider;min=1;max=15;default=1;\n"
    "name=TRANSY_SENSITIVITY;type=slider;min=1;max=15;default=1;\n"
    "name=POS_TRANSZ_SENSITIVITY;type=slider;min=1;max=15;default=2;\n"
    "name=NEG_TRANSZ_SENSITIVITY;type=slider;min=1;max=15;default=1;\n"
    "name=GATE_NEG_TRANSZ;type=slider;min=1;max=30;default=5;\n"
    "name=GATE_ROTX;type=slider;min=1;max=30;default=10;\n"
    "name=GATE_ROTY;type=slider;min=1;max=30;default=10;\n"
    "name=GATE_ROTZ;type=slider;min=1;max=30;default=5;\n"
    "name=ROTX_SENSITIVITY;type=slider;min=1;max=15;default=1;\n"
    "name=ROTY_SENSITIVITY;type=slider;min=1;max=15;default=1;\n"
    "name=ROTZ_SENSITIVITY;type=slider;min=1;max=15;default=1;\n"; // Don't forget ";" on last line
    Serial.print(ui_values);
    return ui_values;
}
```
</details>

And it will also change sensitivity when a new value is sent through serial:
<details>
  <summary>Show code</summary>

```c++
// raulpetru -- process input received through Serial
String inputString;

void processPair(String pair) {
    // Find the position of the '=' sign
    int separatorIndex = pair.indexOf('=');

    // Split the string into key and value
    String key = pair.substring(0, separatorIndex);
    String value = pair.substring(separatorIndex + 1);

    // Use the results
    if (key == "GET_UI") {
      return_ui();
    }
    if (key == "TRANSX_SENSITIVITY") {
        TRANSX_SENSITIVITY = value.toFloat();
    }
    if (key == "TRANSY_SENSITIVITY") {
        TRANSY_SENSITIVITY = value.toFloat();
    }
    if (key == "POS_TRANSZ_SENSITIVITY") {
        POS_TRANSZ_SENSITIVITY = value.toFloat();
    }
    if (key == "NEG_TRANSZ_SENSITIVITY") {
        NEG_TRANSZ_SENSITIVITY = value.toFloat();
    }
    if (key == "GATE_NEG_TRANSZ") {
        GATE_NEG_TRANSZ = value.toFloat();
    }
    if (key == "GATE_ROTX") {
        GATE_ROTX = value.toFloat();
    }
    if (key == "GATE_ROTY") {
        GATE_ROTY = value.toFloat();
    }
    if (key == "GATE_ROTZ") {
        GATE_ROTZ = value.toFloat();
    }
    if (key == "ROTX_SENSITIVITY") {
        ROTX_SENSITIVITY = value.toFloat();
    }
    if (key == "ROTY_SENSITIVITY") {
        ROTY_SENSITIVITY = value.toFloat();
    }
    if (key == "ROTZ_SENSITIVITY") {
        ROTZ_SENSITIVITY = value.toFloat();
    }
}
```

```c++
void loop() {

    ...

    if (Serial.available()) {
        inputString = Serial.readStringUntil('\n');  // Read the input string

        // Split the string by commas
        int startIndex = 0;
        int endIndex = inputString.indexOf(',');

        while (endIndex != -1) {
            String pair = inputString.substring(startIndex, endIndex);
            processPair(pair);
            startIndex = endIndex + 1;
            endIndex = inputString.indexOf(',', startIndex);
        }

        // Process the last pair (or the only pair if no commas were found)
        String lastPair = inputString.substring(startIndex);
        processPair(lastPair);
    }
    
    ...  
    
  }
```
</details>

[Check out the file for all changes.](https://github.com/raulpetru/DIY_SpaceMouse_Profiles/blob/master/SpaceMouse%20Firmwares/HE_Spacemouse/HE_Spacemouse.ino)

**_There are quite a few firmwares available and, they can be fairly easily modified to work with this UI application._**

# Instructions
## Set up SpaceMouse
**_IMPORTANT:_** The firmware included in this repo is a modified version of [ChromeBee's Hall-Effect-Sensor-CAD-Mouse-Spacemouse](https://github.com/ChromeBee/Hall-Effect-Sensor-CAD-Mouse-Spacemouse/tree/main), so this firmware will only work with that specific hardware.
1. Clone this repository:  
`git clone https://github.com/raulpetru/DIY_SpaceMouse_Profiles.git`
2. Create a custom board in Arduino IDE using [these instructions](https://github.com/AndunHH/spacemouse/wiki/Creating-a-custom-board-for-Arduino-IDE).
3. Connect SpaceMouse to PC and flash firmware `SpaceMouse Firmwares/HE_Spacemouse/HE_Spacemouse.ino` on Arduino.

## Set up DIY SpaceMouse Profiles application
1. Download [latest release](https://github.com/raulpetru/DIY_SpaceMouse_Profiles/releases).
2. Connect your DIY SpaceMouse to PC (else the application won't start).
3. (Recommended) Create a folder `DIY SpaceMouse Profiles` and place the downloaded .exe inside.
4. Run `DIY_SpaceMouse_Profiles.exe`

This project is based on the work of [ChromeBee](https://github.com/ChromeBee), [AndunHH](https://github.com/AndunHH/spacemouse), [TeachingTech](https://www.printables.com/de/model/864950-open-source-spacemouse-space-mushroom-remix) and many other contributors.