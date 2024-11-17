
# Description

<p align="center">
  <img src="https://github.com/user-attachments/assets/014b1838-8ab1-4964-9dc9-f9f4e3577095" width=33%>
  <img src="https://github.com/user-attachments/assets/ebb540b8-f2df-4363-97a6-aa19606f2d16" width=33%>
  <img src="https://github.com/user-attachments/assets/aec96826-6b83-4e90-bdca-509b5fe2e851" width=33%>
</p>

DIY SpaceMouse Profiles builds a user interface based on values requested from the DIY SpaceMouse.

The firmware provided in this repository is modified to send through serial information to build the UI:
<details>
  <summary>Show code</summary>

```c++
void return_ui() {
    const char * ui_values=
    "name=DEADZONE;send_name=dz;type=slider;tab=Deadzone;min=0;max=350;default=55;\n"
    "name=TRANSX_SENSITIVITY;send_name=tsx;tab=Sensitivity;type=slider;min=1;max=30;default=5;\n"
    "name=TRANSY_SENSITIVITY;send_name=tsy;tab=Sensitivity;type=slider;min=1;max=30;default=5;\n"
    "name=POS_TRANSZ_SENSITIVITY;send_name=ptsy;tab=Sensitivity;type=slider;min=1;max=30;default=5;\n"
    "name=NEG_TRANSZ_SENSITIVITY;send_name=ntsy;tab=Sensitivity;type=slider;min=1;max=30;default=5;\n"
    "name=GATE_POS_TRANSZ;send_name=gptz;tab=Deadzone;type=slider;min=0;max=350;default=0;\n"
    "name=GATE_NEG_TRANSZ;send_name=gntz;tab=Deadzone;type=slider;min=0;max=350;default=0;\n"
    "name=GATE_ROTX;send_name=grx;tab=Deadzone;type=slider;min=0;max=350;default=50;\n"
    "name=GATE_ROTY;send_name=gry;tab=Deadzone;type=slider;min=0;max=350;default=50;\n"
    "name=GATE_ROTZ;send_name=grz;tab=Deadzone;type=slider;min=0;max=350;default=50;\n"
    "name=ROTX_SENSITIVITY;send_name=rtsx;tab=Sensitivity;type=slider;min=1;max=30;default=5;\n"
    "name=ROTY_SENSITIVITY;send_name=rtsy;tab=Sensitivity;type=slider;min=1;max=30;default=5;\n"
    "name=ROTZ_SENSITIVITY;send_name=rtsz;tab=Sensitivity;type=slider;min=1;max=30;default=5;\n"
    "name=invX;send_name=invx;tab=Invert directions;type=bool;default=0;\n" // For bool values use 0 for False, 1 for True
    "name=invY;send_name=invy;tab=Invert directions;type=bool;default=0;\n"
    "name=invZ;send_name=invz;tab=Invert directions;type=bool;default=0;\n"
    "name=invRX;send_name=invrx;tab=Invert directions;type=bool;default=0;\n"
    "name=invRY;send_name=invry;tab=Invert directions;type=bool;default=0;\n"
    "name=invRZ;send_name=invrz;tab=Invert directions;type=bool;default=0;\n"; // Don't forget ";" on last line
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
    if (key == "dz") {
        DEADZONE = value.toFloat();
    }
    if (key == "tsx") {
        TRANSX_SENSITIVITY = (value.toFloat()/10); // Divide the value received through UI by 10 to obtain a more accurate sensitivity control.
    }
    if (key == "tsy") {
        TRANSY_SENSITIVITY = (value.toFloat()/10);
    }
    if (key == "ptsy") {
        POS_TRANSZ_SENSITIVITY = (value.toFloat()/10);
    }
    if (key == "ntsy") {
        NEG_TRANSZ_SENSITIVITY = (value.toFloat()/10);
    }
    if (key == "gptz") {
        GATE_POS_TRANSZ = value.toFloat();
    }
    if (key == "gntz") {
        GATE_NEG_TRANSZ = value.toFloat();
    }
    if (key == "grx") {
        GATE_ROTX = value.toFloat();
    }
    if (key == "gry") {
        GATE_ROTY = value.toFloat();
    }
    if (key == "grz") {
        GATE_ROTZ = value.toFloat();
    }
    if (key == "rtsx") {
        ROTX_SENSITIVITY = (value.toFloat()/10);
    }
    if (key == "rtsy") {
        ROTY_SENSITIVITY = (value.toFloat()/10);
    }
    if (key == "rtsz") {
        ROTZ_SENSITIVITY = (value.toFloat()/10);
    }
    if (key == "invx") {
        invX = (value.toInt() == 1) ? true : false;
    }
    if (key == "invy") {
        invY = (value.toInt() == 1) ? true : false;
    }
    if (key == "invz") {
        invZ = (value.toInt() == 1) ? true : false;
    }
    if (key == "invrx") {
        invRX = (value.toInt() == 1) ? true : false;
    }
    if (key == "invry") {
        invRY = (value.toInt() == 1) ? true : false;
    }
    if (key == "invrz") {
        invRZ = (value.toInt() == 1) ? true : false;
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

**_There are quite a few firmwares available around and they can be fairly easily modified to work with this UI application._**

# Instructions
## Set up SpaceMouse
**_IMPORTANT:_** The firmware included in this repo is a modified version of [ChromeBee's Hall-Effect-Sensor-CAD-Mouse-Spacemouse](https://github.com/ChromeBee/Hall-Effect-Sensor-CAD-Mouse-Spacemouse/tree/main), so this firmware will only work with that specific hardware.
1. Clone this repository:  
`git clone https://github.com/raulpetru/DIY_SpaceMouse_Profiles.git`
2. Create a custom board in Arduino IDE using [these instructions](https://github.com/AndunHH/spacemouse/wiki/Creating-a-custom-board-for-Arduino-IDE).
3. Connect SpaceMouse to PC and flash firmware `SpaceMouse Firmwares/HE_Spacemouse/HE_Spacemouse.ino` on Arduino.

## Set up DIY SpaceMouse Profiles application
1. Download [latest release](https://github.com/raulpetru/DIY_SpaceMouse_Profiles/releases).
2. Connect your DIY SpaceMouse to PC (__else the application won't start__).
3. (Recommended) Create a folder `DIY SpaceMouse Profiles` and place the downloaded .exe inside.
4. Run `DIY_SpaceMouse_Profiles.exe`

This project is based on the work of [ChromeBee](https://github.com/ChromeBee), [AndunHH](https://github.com/AndunHH/spacemouse), [TeachingTech](https://www.printables.com/de/model/864950-open-source-spacemouse-space-mushroom-remix) and many other contributors.
